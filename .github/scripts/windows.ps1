param(
  [Parameter(Mandatory)]
  [ValidateSet('prepare', 'collect', 'verify')]
  [string] $Phase
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$binary = 'Input Scope.4DX'

function Assert-PlainItem($Item) {
  if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw "Refusing reparse point: $($Item.FullName)"
  }
}

# Resolve each component, not a recursive first match. This also follows the
# committed casing on case-sensitive hosts while matching Windows semantics.
function Resolve-SafePath([string] $Relative) {
  $path = $root
  $parts = $Relative.Split('/')
  Assert-PlainItem (Get-Item -LiteralPath $path -Force)
  for ($i = 0; $i -lt $parts.Count; $i++) {
    $matches = @(Get-ChildItem -LiteralPath $path -Force |
      Where-Object { $_.Name -ieq $parts[$i] })
    if ($matches.Count -gt 1) { throw "Ambiguous Windows path: $Relative" }
    if ($matches.Count -eq 0) {
      for (; $i -lt $parts.Count; $i++) { $path = Join-Path $path $parts[$i] }
      return $path
    }
    $item = $matches[0]
    Assert-PlainItem $item
    if ($i -lt $parts.Count - 1 -and -not $item.PSIsContainer) {
      throw "Expected directory: $($item.FullName)"
    }
    $path = $item.FullName
  }
  return $path
}

function Assert-PlainTree([string] $Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return }
  $item = Get-Item -LiteralPath $Path -Force
  Assert-PlainItem $item
  if ($item.PSIsContainer) {
    foreach ($child in Get-ChildItem -LiteralPath $Path -Force) {
      Assert-PlainItem $child
      if ($child.PSIsContainer) { Assert-PlainTree $child.FullName }
    }
  }
}

function Assert-File([string] $Path) {
  $item = Get-Item -LiteralPath $Path -Force
  Assert-PlainItem $item
  if ($item.PSIsContainer -or $item.Length -eq 0) {
    throw "Expected nonempty file: $Path"
  }
}

$ancestor = Get-Item -LiteralPath $root -Force
while ($null -ne $ancestor) {
  Assert-PlainItem $ancestor
  $ancestor = $ancestor.Parent
}

$output = Resolve-SafePath 'test/plugins/Input Scope.bundle/contents/windows64/Input Scope.4DX'
$intermediate = Resolve-SafePath 'Objs/Release'
$stage = Resolve-SafePath 'winbin'

switch ($Phase) {
  'prepare' {
    # Validate every deletion target before deleting even the first file.
    Assert-PlainTree $output
    Assert-PlainTree $intermediate
    if ((Test-Path -LiteralPath $output) -and
        (Get-Item -LiteralPath $output -Force).PSIsContainer) {
      throw "Expected binary file: $output"
    }
    if ((Test-Path -LiteralPath $intermediate) -and
        -not (Get-Item -LiteralPath $intermediate -Force).PSIsContainer) {
      throw "Expected intermediate directory: $intermediate"
    }
    if (Test-Path -LiteralPath $output) {
      Remove-Item -LiteralPath $output -Force
    }
    if (Test-Path -LiteralPath $intermediate) {
      Remove-Item -LiteralPath $intermediate -Recurse -Force
    }
  }
  'collect' {
    Assert-File $output
    Assert-PlainTree $stage
    if (Test-Path -LiteralPath $stage) {
      if (-not (Get-Item -LiteralPath $stage -Force).PSIsContainer) {
        throw "Expected staging directory: $stage"
      }
      foreach ($item in Get-ChildItem -LiteralPath $stage -Force) {
        if ($item.PSIsContainer -or $item.Name -ne $binary) {
          throw "Unexpected staging entry: $($item.FullName)"
        }
      }
    } else {
      New-Item -ItemType Directory -Path $stage | Out-Null
    }
    foreach ($path in @($output)) {
      $destination = Resolve-SafePath "winbin/$([IO.Path]::GetFileName($path))"
      Copy-Item -LiteralPath $path -Destination $destination -Force
      Assert-File $destination
    }
  }
  'verify' {
    Assert-PlainTree $stage
    foreach ($name in @($binary)) {
      Assert-File (Resolve-SafePath "winbin/$name")
    }
    foreach ($item in Get-ChildItem -LiteralPath $stage -Force) {
      if ($item.PSIsContainer -or $item.Name -ne $binary) {
        throw "Unexpected staging entry: $($item.FullName)"
      }
    }
  }
}

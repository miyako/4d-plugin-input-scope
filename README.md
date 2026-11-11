![version](https://img.shields.io/badge/version-17%2B-3E8B93)
![platform](https://img.shields.io/static/v1?label=platform&message=win-64&color=blue)
[![license](https://img.shields.io/github/license/miyako/4d-plugin-input-scope)](LICENSE)
![downloads](https://img.shields.io/github/downloads/miyako/4d-plugin-input-scope/total)

# 4d-plugin-input-scope
入力スコープ（半角・全角・ひらがな etc.）を切り替えます。

### Syntax

[miyako.github.io](https://miyako.github.io/2019/07/25/4d-plugin-input-scope.html)

---

## Command reference

Switches the Windows IME for the focused window. For the Japanese scopes the plugin sets the IME mode directly through IMM32 (`ImmSetOpenStatus` / `ImmSetConversionStatus`); for every scope it also passes the value to `SetInputScope` (from `msctf.dll`) as a hint to the IME.

| Command | Returns | Purpose |
|---|---|---|
| [Set input scope](#set-input-scope) | `Longint` | Re-enable the IME and switch its mode or input-scope hint |
| [Disable input method](#disable-input-method) | `Longint` | Turn the IME off for the focused window |

**Platforms:** Windows 64-bit. On macOS both commands do nothing and return `0`.

---

## Requirements & platform notes

- **The commands act on the whole window, not on one form object.** They use the window that has keyboard focus (`GetFocus`), and 4D form objects are not separate windows. The setting stays until the next call, so call the command in `On getting focus` of each field that needs a specific mode.
- **The IME modes are set only with a Japanese keyboard layout.** With another layout, `Set input scope` only passes the hint.
- **Failure is reported by the return value, not by a 4D error.**

---

## Set input scope

### Syntax

```
Set input scope ( scope ) -> Longint
```

| Parameter | Type | Description |
|---|---|---|
| `scope` | `Longint` | One of the `IS_*` constants in the `Input Scope` theme |
| Result | `Longint` | `0` on success, otherwise a negative Windows `HRESULT` |

### Description

The command cancels any composition in progress. If `Disable input method` turned the IME off for the window, the IME is turned back on.

With a Japanese keyboard layout these scopes switch the IME mode immediately:

| Scope | IME mode |
|---|---|
| `IS_HIRAGANA` | On, full-width hiragana |
| `IS_KATAKANA_FULLWIDTH` | On, full-width katakana |
| `IS_KATAKANA_HALFWIDTH` | On, half-width katakana |
| `IS_ALPHANUMERIC_FULLWIDTH`, `IS_NUMBER_FULLWIDTH` | On, full-width alphanumeric |
| `IS_ALPHANUMERIC_HALFWIDTH` | Off (direct input) |

Other settings of the IME, such as romaji or kana input, are kept.

Every other scope is only passed to `SetInputScope`. The IME usually reads that hint when focus enters the window, so it may not change the mode of an IME that is already active.

`IS_PHRASELIST`, `IS_REGULAREXPRESSION`, `IS_SRGS`, `IS_XML` and `IS_ENUMSTRING` are not supported and return `E_INVALIDARG` (`-2147024809`). In earlier versions these constants had wrong values (69 to 73); they now match the Windows SDK (-1 to -5).

### Example

From the plugin's own test form:

```4d
$result:=Set input scope (IS_HIRAGANA)
```

---

## Disable input method

### Syntax

```
Disable input method -> Longint
```

| Parameter | Type | Description |
|---|---|---|
| Result | `Longint` | `1` on success, `0` on failure |

### Description

Cancels any composition in progress, resets the input-scope hint and turns the IME off for the focused window. The IME stays off until `Set input scope` is called for that window.

The result uses `1` for success, unlike `Set input scope`; this is unchanged from earlier versions.

---

## Error handling & troubleshooting

- **`-2147023496` (`ERROR_INVALID_WINDOW_HANDLE`) from `Set input scope`:** no window had keyboard focus. `Disable input method` returns `0` in the same case.
- **`-2147467263` (`E_NOTIMPL`):** `msctf.dll` or its `SetInputScope` export was not available, and the scope has no IME mode the plugin can set directly.
- **`-2147467259` (`E_FAIL`):** the IME rejected the open status or conversion mode.
- **The mode carries over to other fields:** the setting applies to the window. Call `Set input scope` again (for example with `IS_DEFAULT`) in `On getting focus` of the other fields.

### Manual workflows

**Bump version** updates source versions on the selected branch; **Build** is a
separate manual action with no custom inputs. The existing `v2.0.3` is occupied,
so run Bump separately before building a new release. See the
[workflow and recovery guide](.github/README.md).

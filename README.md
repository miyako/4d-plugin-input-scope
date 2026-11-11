# Input Scope

English | [日本語](README.ja.md)

Switches the Windows IME (input method) of the focused 4D window, for example to hiragana, full-width katakana or half-width alphanumeric input. For the Japanese modes the plugin sets the IME directly with IMM32 (`ImmSetOpenStatus` / `ImmSetConversionStatus`). For every input scope it also passes the value to the Windows `SetInputScope` API as a hint to the IME.

## Requirements

- 4D v17 or later
- Windows 64-bit. On macOS the commands do nothing and return `0`.
- A Japanese keyboard layout (Microsoft IME or another IME) for the commands to switch the IME mode directly

## Installation

Download the latest release from the [Releases](../../releases) page.

### macOS & Windows (single download)

1. Download the `.zip` from the release
2. Extract to get the `Input Scope.bundle` folder
3. Copy the `.bundle` into your 4D application's **Plugins** folder (or your database's **Plugins** folder)
4. Restart 4D

### macOS only (notarized DMG)

1. Download the `.dmg` from the release
2. Mount it and copy the `.bundle` into your **Plugins** folder
3. Restart 4D

## Commands

Both commands act on the window that has keyboard focus, not on a single form object, because 4D form objects are not separate Windows windows. The setting stays until the next call, so call the command in the `On getting focus` event of each field that needs a specific mode. Failure is reported by the return value, never by a 4D error.

### `Set input scope`

```4d
$result:=Set input scope($scope)
```

| Parameter | Type | Description |
|---|---|---|
| `$scope` | Longint | One of the `IS_*` constants (see [Constants](#constants)) |
| `$result` | Longint | `0` on success, otherwise a negative Windows `HRESULT` |

The command cancels any text being composed. If `Disable input method` turned the IME off for the window, it turns the IME back on.

With a Japanese keyboard layout these scopes switch the IME mode immediately. Other IME settings, such as romaji or kana input, are kept.

| Scope | IME mode |
|---|---|
| `IS_HIRAGANA` | On, full-width hiragana |
| `IS_KATAKANA_FULLWIDTH` | On, full-width katakana |
| `IS_KATAKANA_HALFWIDTH` | On, half-width katakana |
| `IS_ALPHANUMERIC_FULLWIDTH`, `IS_NUMBER_FULLWIDTH` | On, full-width alphanumeric |
| `IS_ALPHANUMERIC_HALFWIDTH` | Off (direct input) |

Every other scope is only passed to `SetInputScope`. The IME usually reads that hint when focus enters the window, so it may not change the mode of an IME that is already active.

| `$result` | Meaning |
|---|---|
| `0` | Success |
| `-2147024809` (`E_INVALIDARG`) | `$scope` is not supported: out of range, or one of `IS_PHRASELIST`, `IS_REGULAREXPRESSION`, `IS_SRGS`, `IS_XML`, `IS_ENUMSTRING` |
| `-2147023496` (`ERROR_INVALID_WINDOW_HANDLE`) | No window had keyboard focus |
| `-2147467263` (`E_NOTIMPL`) | `SetInputScope` is not available on this system, and the scope has no IME mode the plugin can set directly |
| `-2147467259` (`E_FAIL`) | The IME rejected the open status or conversion mode |

**Example:**

From the plugin's test form (`test/Project`):

```4d
$result:=Set input scope (IS_HIRAGANA)
```

Set the mode when a field gets focus, in the field's object method (`Form event code` needs 4D v18 or later; use `Form event` in v17):

```4d
If (Form event code=On getting focus)
	$result:=Set input scope(IS_KATAKANA_FULLWIDTH)
End if
```

### `Disable input method`

```4d
$result:=Disable input method
```

| Parameter | Type | Description |
|---|---|---|
| `$result` | Longint | `1` on success, `0` on failure (for example when no window has keyboard focus) |

Cancels any text being composed, resets the input-scope hint and turns the IME off for the focused window. The IME stays off until `Set input scope` is called for that window. Unlike `Set input scope`, the result uses `1` for success; this is unchanged from earlier versions.

**Example:**

```4d
$result:=Disable input method
ASSERT($result=1)
```

## Constants

Theme **Input Scope**. The values are the Windows `InputScope` values. Scopes marked *IME mode* switch the IME directly with a Japanese keyboard layout; the others are hints.

| Constant | Type | Value | Description |
|---|---|---|---|
| `IS_DEFAULT` | Longint | 0 | No specific input (clears the hint) |
| `IS_URL` | Longint | 1 | URL |
| `IS_FILE_FULLFILEPATH` | Longint | 2 | Full file path |
| `IS_FILE_FILENAME` | Longint | 3 | File name |
| `IS_EMAIL_USERNAME` | Longint | 4 | E-mail user name |
| `IS_EMAIL_SMTPEMAILADDRESS` | Longint | 5 | E-mail address |
| `IS_LOGINNAME` | Longint | 6 | Login name |
| `IS_PERSONALNAME_FULLNAME` | Longint | 7 | Full name |
| `IS_PERSONALNAME_PREFIX` | Longint | 8 | Name prefix (title) |
| `IS_PERSONALNAME_GIVENNAME` | Longint | 9 | Given name |
| `IS_PERSONALNAME_MIDDLENAME` | Longint | 10 | Middle name |
| `IS_PERSONALNAME_SURNAME` | Longint | 11 | Surname |
| `IS_PERSONALNAME_SUFFIX` | Longint | 12 | Name suffix |
| `IS_ADDRESS_FULLPOSTALADDRESS` | Longint | 13 | Full postal address |
| `IS_ADDRESS_POSTALCODE` | Longint | 14 | Postal code |
| `IS_ADDRESS_STREET` | Longint | 15 | Street |
| `IS_ADDRESS_STATEORPROVINCE` | Longint | 16 | State or province |
| `IS_ADDRESS_CITY` | Longint | 17 | City |
| `IS_ADDRESS_COUNTRYNAME` | Longint | 18 | Country name |
| `IS_ADDRESS_COUNTRYSHORTNAME` | Longint | 19 | Country code |
| `IS_CURRENCY_AMOUNTANDSYMBOL` | Longint | 20 | Amount with currency symbol |
| `IS_CURRENCY_AMOUNT` | Longint | 21 | Amount |
| `IS_DATE_FULLDATE` | Longint | 22 | Full date |
| `IS_DATE_MONTH` | Longint | 23 | Month (number) |
| `IS_DATE_DAY` | Longint | 24 | Day |
| `IS_DATE_YEAR` | Longint | 25 | Year |
| `IS_DATE_MONTHNAME` | Longint | 26 | Month name |
| `IS_DATE_DAYNAME` | Longint | 27 | Day name |
| `IS_DIGITS` | Longint | 28 | Digits |
| `IS_NUMBER` | Longint | 29 | Number |
| `IS_ONECHAR` | Longint | 30 | Single character |
| `IS_PASSWORD` | Longint | 31 | Password |
| `IS_TELEPHONE_FULLTELEPHONENUMBER` | Longint | 32 | Full telephone number |
| `IS_TELEPHONE_COUNTRYCODE` | Longint | 33 | Telephone country code |
| `IS_TELEPHONE_AREACODE` | Longint | 34 | Area code |
| `IS_TELEPHONE_LOCALNUMBER` | Longint | 35 | Local number |
| `IS_TIME_FULLTIME` | Longint | 36 | Full time |
| `IS_TIME_HOUR` | Longint | 37 | Hour |
| `IS_TIME_MINORSEC` | Longint | 38 | Minutes or seconds |
| `IS_NUMBER_FULLWIDTH` | Longint | 39 | Full-width number. *IME mode*: full-width alphanumeric |
| `IS_ALPHANUMERIC_HALFWIDTH` | Longint | 40 | Half-width alphanumeric. *IME mode*: off |
| `IS_ALPHANUMERIC_FULLWIDTH` | Longint | 41 | Full-width alphanumeric. *IME mode*: full-width alphanumeric |
| `IS_CURRENCY_CHINESE` | Longint | 42 | Chinese currency |
| `IS_BOPOMOFO` | Longint | 43 | Bopomofo |
| `IS_HIRAGANA` | Longint | 44 | Hiragana. *IME mode*: full-width hiragana |
| `IS_KATAKANA_HALFWIDTH` | Longint | 45 | Half-width katakana. *IME mode*: half-width katakana |
| `IS_KATAKANA_FULLWIDTH` | Longint | 46 | Full-width katakana. *IME mode*: full-width katakana |
| `IS_HANJA` | Longint | 47 | Hanja |
| `IS_HANGUL_HALFWIDTH` | Longint | 48 | Half-width Hangul |
| `IS_HANGUL_FULLWIDTH` | Longint | 49 | Full-width Hangul |
| `IS_SEARCH` | Longint | 50 | Search |
| `IS_FORMULA` | Longint | 51 | Spreadsheet formula |
| `IS_SEARCH_INCREMENTAL` | Longint | 52 | Incremental search |
| `IS_CHINESE_HALFWIDTH` | Longint | 53 | Half-width Chinese |
| `IS_CHINESE_FULLWIDTH` | Longint | 54 | Full-width Chinese |
| `IS_NATIVE_SCRIPT` | Longint | 55 | Native script |
| `IS_YOMI` | Longint | 56 | Japanese reading (yomi) |
| `IS_TEXT` | Longint | 57 | Text |
| `IS_CHAT` | Longint | 58 | Chat |
| `IS_NAME_OR_PHONENUMBER` | Longint | 59 | Name or telephone number |
| `IS_EMAILNAME_OR_ADDRESS` | Longint | 60 | E-mail name or address |
| `IS_PRIVATE` | Longint | 61 | Private (input is not learned) |
| `IS_MAPS` | Longint | 62 | Map location |
| `IS_NUMERIC_PASSWORD` | Longint | 63 | Numeric password |
| `IS_NUMERIC_PIN` | Longint | 64 | Numeric PIN |
| `IS_ALPHANUMERIC_PIN` | Longint | 65 | Alphanumeric PIN |
| `IS_ALPHANUMERIC_PIN_SET` | Longint | 66 | Alphanumeric PIN (setting a new one) |
| `IS_FORMULA_NUMBER` | Longint | 67 | Number in a formula |
| `IS_CHAT_WITHOUT_EMOJI` | Longint | 68 | Chat without emoji |
| `IS_PHRASELIST` | Longint | -1 | Not supported: returns `E_INVALIDARG` |
| `IS_REGULAREXPRESSION` | Longint | -2 | Not supported: returns `E_INVALIDARG` |
| `IS_SRGS` | Longint | -3 | Not supported: returns `E_INVALIDARG` |
| `IS_XML` | Longint | -4 | Not supported: returns `E_INVALIDARG` |
| `IS_ENUMSTRING` | Longint | -5 | Not supported: returns `E_INVALIDARG` |

In version 2.0.3 and earlier, `IS_PHRASELIST` to `IS_ENUMSTRING` had the wrong values 69 to 73.

## Building from Source

### Prerequisites

- Xcode (macOS)
- Visual Studio 2022 with the v143 toolset and the Windows 10 SDK (Windows)

### Clone

```bash
git clone https://github.com/miyako/4d-plugin-input-scope.git
cd 4d-plugin-input-scope
```

### Build (macOS)

```bash
xcodebuild -project "Input Scope.xcodeproj" -target "Input Scope" -configuration Default ARCHS="arm64 x86_64" ONLY_ACTIVE_ARCH=NO CODE_SIGNING_ALLOWED=NO build
```

### Build (Windows)

```pwsh
msbuild "Input Scope.sln" /p:Configuration=Release /p:Platform=x64 /p:PlatformToolset=v143 /p:WindowsTargetPlatformVersion=10.0 /m
```

### Run Tests

The plugin changes the IME of a focused window, so it is tested by hand on Windows:

1. Build the plugin and copy it into `test/Plugins`
2. Open `test/Project/test.4DProject` in 4D
3. Run the `TEST` method, click a field in the form, then click the buttons to switch the IME mode

## CI/CD

This project uses two manual workflows. See the [workflow and recovery guide](.github/README.md) for details.

| Workflow | Trigger | Purpose |
|---|---|---|
| `bump-version.yml` (**Bump version**) | Manual, any branch; input `patch`, `minor` or `major` | Bump the source version and commit; no build or tag |
| `release.yml` (**Build**) | Manual, any ref; no inputs | Build Windows x64 and macOS universal, sign, notarize, and publish the `.zip` and `.dmg` release |

A release tag that already exists is not overwritten: run **Bump version** before **Build**.

### Required Secrets (for `release.yml` only)

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `APPLE_DEVELOPER_ID_CERTIFICATE` | Base64-encoded Developer ID Application `.p12` including its private key |
| `APPLE_DEVELOPER_ID_CERTIFICATE_PASSWORD` | Password for the `.p12` export |
| `KEYCHAIN_PASSWORD` | Independent password for the CI runner's temporary keychain |
| `NOTARYTOOL_APPLE_ID` | Apple ID email for notarization |
| `NOTARYTOOL_TEAM_ID` | Apple Developer Team ID (10-char alphanumeric) |
| `NOTARYTOOL_PASSWORD` | Apple app-specific password, not the account password |

## License

MIT. See [LICENSE](LICENSE).

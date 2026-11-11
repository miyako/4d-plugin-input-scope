# Input Scope

[English](README.md) | 日本語

フォーカスのある 4D ウインドウの Windows IME（日本語入力）を、ひらがな・全角カタカナ・半角英数などに切り替えます。日本語のモードは IMM32（`ImmSetOpenStatus` / `ImmSetConversionStatus`）で IME を直接設定します。すべての入力スコープは、IME へのヒントとして Windows の `SetInputScope` API にも渡します。

## 動作条件

- 4D v17 以降
- Windows 64-bit。macOS ではコマンドは何もせず `0` を返します。
- IME のモードを直接切り替えるには日本語キーボードレイアウト（Microsoft IME などの IME）が必要です

## インストール

[Releases](../../releases) ページから最新のリリースをダウンロードします。

### macOS & Windows（共通ダウンロード）

1. リリースから `.zip` をダウンロードします
2. 展開して `Input Scope.bundle` フォルダーを取り出します
3. `.bundle` を 4D アプリケーションの **Plugins** フォルダー（またはデータベースの **Plugins** フォルダー）にコピーします
4. 4D を再起動します

### macOS のみ（公証済み DMG）

1. リリースから `.dmg` をダウンロードします
2. マウントして `.bundle` を **Plugins** フォルダーにコピーします
3. 4D を再起動します

## コマンド

4D のフォームオブジェクトは個別の Windows ウインドウではないため、どちらのコマンドも個々のフォームオブジェクトではなく、キーボードフォーカスのあるウインドウ全体に作用します。設定は次に呼び出すまで残るので、特定のモードが必要な各フィールドの `On getting focus` イベントでコマンドを呼び出してください。失敗は戻り値で返され、4D のエラーにはなりません。

### `Set input scope`

```4d
$result:=Set input scope($scope)
```

| 引数 | 型 | 説明 |
|---|---|---|
| `$scope` | 倍長整数 | `IS_*` 定数のいずれか（[定数](#定数)を参照） |
| `$result` | 倍長整数 | 成功時は `0`、それ以外は負の Windows `HRESULT` |

変換中の文字列を取り消します。`Disable input method` でウインドウの IME がオフになっていた場合は、IME をオンに戻します。

日本語キーボードレイアウトでは、次のスコープで IME のモードがすぐに切り替わります。ローマ字入力・かな入力など、IME のほかの設定はそのまま保たれます。

| スコープ | IME のモード |
|---|---|
| `IS_HIRAGANA` | オン、全角ひらがな |
| `IS_KATAKANA_FULLWIDTH` | オン、全角カタカナ |
| `IS_KATAKANA_HALFWIDTH` | オン、半角カタカナ |
| `IS_ALPHANUMERIC_FULLWIDTH`, `IS_NUMBER_FULLWIDTH` | オン、全角英数 |
| `IS_ALPHANUMERIC_HALFWIDTH` | オフ（直接入力） |

それ以外のスコープは `SetInputScope` に渡すだけです。IME はふつうフォーカスがウインドウに入ったときにこのヒントを読むため、すでに動作中の IME のモードは変わらないことがあります。

| `$result` | 意味 |
|---|---|
| `0` | 成功 |
| `-2147024809` (`E_INVALIDARG`) | `$scope` に対応していません。範囲外の値、または `IS_PHRASELIST`、`IS_REGULAREXPRESSION`、`IS_SRGS`、`IS_XML`、`IS_ENUMSTRING` のいずれかです |
| `-2147023496` (`ERROR_INVALID_WINDOW_HANDLE`) | キーボードフォーカスのあるウインドウがありません |
| `-2147467263` (`E_NOTIMPL`) | このシステムでは `SetInputScope` を使えず、そのスコープにはプラグインが直接設定できる IME モードがありません |
| `-2147467259` (`E_FAIL`) | IME がオン・オフ状態または変換モードの設定を受け付けませんでした |

**例:**

プラグインのテストフォーム（`test/Project`）より:

```4d
$result:=Set input scope (IS_HIRAGANA)
```

フィールドのオブジェクトメソッドで、フォーカスを得たときにモードを設定します（`Form event code` は 4D v18 以降。v17 では `Form event` を使用します）:

```4d
If (Form event code=On getting focus)
	$result:=Set input scope(IS_KATAKANA_FULLWIDTH)
End if
```

### `Disable input method`

```4d
$result:=Disable input method
```

| 引数 | 型 | 説明 |
|---|---|---|
| `$result` | 倍長整数 | 成功時は `1`、失敗時は `0`（キーボードフォーカスのあるウインドウがない場合など） |

変換中の文字列を取り消し、入力スコープのヒントをリセットして、フォーカスのあるウインドウの IME をオフにします。IME はそのウインドウで `Set input scope` を呼び出すまでオフのままです。`Set input scope` と異なり、戻り値は成功時に `1` です。これは以前のバージョンから変わっていません。

**例:**

```4d
$result:=Disable input method
ASSERT($result=1)
```

## 定数

テーマ **Input Scope**。値は Windows の `InputScope` の値です。*IME モード* と書かれたスコープは、日本語キーボードレイアウトで IME を直接切り替えます。それ以外はヒントです。

| 定数 | 型 | 値 | 説明 |
|---|---|---|---|
| `IS_DEFAULT` | 倍長整数 | 0 | 指定なし（ヒントを解除） |
| `IS_URL` | 倍長整数 | 1 | URL |
| `IS_FILE_FULLFILEPATH` | 倍長整数 | 2 | ファイルのフルパス |
| `IS_FILE_FILENAME` | 倍長整数 | 3 | ファイル名 |
| `IS_EMAIL_USERNAME` | 倍長整数 | 4 | メールのユーザー名 |
| `IS_EMAIL_SMTPEMAILADDRESS` | 倍長整数 | 5 | メールアドレス |
| `IS_LOGINNAME` | 倍長整数 | 6 | ログイン名 |
| `IS_PERSONALNAME_FULLNAME` | 倍長整数 | 7 | 氏名 |
| `IS_PERSONALNAME_PREFIX` | 倍長整数 | 8 | 敬称（前置） |
| `IS_PERSONALNAME_GIVENNAME` | 倍長整数 | 9 | 名 |
| `IS_PERSONALNAME_MIDDLENAME` | 倍長整数 | 10 | ミドルネーム |
| `IS_PERSONALNAME_SURNAME` | 倍長整数 | 11 | 姓 |
| `IS_PERSONALNAME_SUFFIX` | 倍長整数 | 12 | 敬称（後置） |
| `IS_ADDRESS_FULLPOSTALADDRESS` | 倍長整数 | 13 | 住所 |
| `IS_ADDRESS_POSTALCODE` | 倍長整数 | 14 | 郵便番号 |
| `IS_ADDRESS_STREET` | 倍長整数 | 15 | 番地 |
| `IS_ADDRESS_STATEORPROVINCE` | 倍長整数 | 16 | 都道府県・州 |
| `IS_ADDRESS_CITY` | 倍長整数 | 17 | 市区町村 |
| `IS_ADDRESS_COUNTRYNAME` | 倍長整数 | 18 | 国名 |
| `IS_ADDRESS_COUNTRYSHORTNAME` | 倍長整数 | 19 | 国コード |
| `IS_CURRENCY_AMOUNTANDSYMBOL` | 倍長整数 | 20 | 通貨記号付きの金額 |
| `IS_CURRENCY_AMOUNT` | 倍長整数 | 21 | 金額 |
| `IS_DATE_FULLDATE` | 倍長整数 | 22 | 日付 |
| `IS_DATE_MONTH` | 倍長整数 | 23 | 月（数字） |
| `IS_DATE_DAY` | 倍長整数 | 24 | 日 |
| `IS_DATE_YEAR` | 倍長整数 | 25 | 年 |
| `IS_DATE_MONTHNAME` | 倍長整数 | 26 | 月名 |
| `IS_DATE_DAYNAME` | 倍長整数 | 27 | 曜日名 |
| `IS_DIGITS` | 倍長整数 | 28 | 数字 |
| `IS_NUMBER` | 倍長整数 | 29 | 数値 |
| `IS_ONECHAR` | 倍長整数 | 30 | 1 文字 |
| `IS_PASSWORD` | 倍長整数 | 31 | パスワード |
| `IS_TELEPHONE_FULLTELEPHONENUMBER` | 倍長整数 | 32 | 電話番号 |
| `IS_TELEPHONE_COUNTRYCODE` | 倍長整数 | 33 | 国番号 |
| `IS_TELEPHONE_AREACODE` | 倍長整数 | 34 | 市外局番 |
| `IS_TELEPHONE_LOCALNUMBER` | 倍長整数 | 35 | 市内番号 |
| `IS_TIME_FULLTIME` | 倍長整数 | 36 | 時刻 |
| `IS_TIME_HOUR` | 倍長整数 | 37 | 時 |
| `IS_TIME_MINORSEC` | 倍長整数 | 38 | 分または秒 |
| `IS_NUMBER_FULLWIDTH` | 倍長整数 | 39 | 全角数字。*IME モード*: 全角英数 |
| `IS_ALPHANUMERIC_HALFWIDTH` | 倍長整数 | 40 | 半角英数。*IME モード*: オフ |
| `IS_ALPHANUMERIC_FULLWIDTH` | 倍長整数 | 41 | 全角英数。*IME モード*: 全角英数 |
| `IS_CURRENCY_CHINESE` | 倍長整数 | 42 | 中国の通貨 |
| `IS_BOPOMOFO` | 倍長整数 | 43 | 注音字母 |
| `IS_HIRAGANA` | 倍長整数 | 44 | ひらがな。*IME モード*: 全角ひらがな |
| `IS_KATAKANA_HALFWIDTH` | 倍長整数 | 45 | 半角カタカナ。*IME モード*: 半角カタカナ |
| `IS_KATAKANA_FULLWIDTH` | 倍長整数 | 46 | 全角カタカナ。*IME モード*: 全角カタカナ |
| `IS_HANJA` | 倍長整数 | 47 | ハンジャ（韓国語の漢字） |
| `IS_HANGUL_HALFWIDTH` | 倍長整数 | 48 | 半角ハングル |
| `IS_HANGUL_FULLWIDTH` | 倍長整数 | 49 | 全角ハングル |
| `IS_SEARCH` | 倍長整数 | 50 | 検索 |
| `IS_FORMULA` | 倍長整数 | 51 | 表計算の数式 |
| `IS_SEARCH_INCREMENTAL` | 倍長整数 | 52 | インクリメンタル検索 |
| `IS_CHINESE_HALFWIDTH` | 倍長整数 | 53 | 半角中国語 |
| `IS_CHINESE_FULLWIDTH` | 倍長整数 | 54 | 全角中国語 |
| `IS_NATIVE_SCRIPT` | 倍長整数 | 55 | ネイティブの文字 |
| `IS_YOMI` | 倍長整数 | 56 | 読み仮名 |
| `IS_TEXT` | 倍長整数 | 57 | テキスト |
| `IS_CHAT` | 倍長整数 | 58 | チャット |
| `IS_NAME_OR_PHONENUMBER` | 倍長整数 | 59 | 名前または電話番号 |
| `IS_EMAILNAME_OR_ADDRESS` | 倍長整数 | 60 | メールの名前またはアドレス |
| `IS_PRIVATE` | 倍長整数 | 61 | プライベート（入力を学習しない） |
| `IS_MAPS` | 倍長整数 | 62 | 地図の場所 |
| `IS_NUMERIC_PASSWORD` | 倍長整数 | 63 | 数字のパスワード |
| `IS_NUMERIC_PIN` | 倍長整数 | 64 | 数字の PIN |
| `IS_ALPHANUMERIC_PIN` | 倍長整数 | 65 | 英数字の PIN |
| `IS_ALPHANUMERIC_PIN_SET` | 倍長整数 | 66 | 英数字の PIN（新規設定） |
| `IS_FORMULA_NUMBER` | 倍長整数 | 67 | 数式内の数値 |
| `IS_CHAT_WITHOUT_EMOJI` | 倍長整数 | 68 | 絵文字なしのチャット |
| `IS_PHRASELIST` | 倍長整数 | -1 | 非対応: `E_INVALIDARG` を返します |
| `IS_REGULAREXPRESSION` | 倍長整数 | -2 | 非対応: `E_INVALIDARG` を返します |
| `IS_SRGS` | 倍長整数 | -3 | 非対応: `E_INVALIDARG` を返します |
| `IS_XML` | 倍長整数 | -4 | 非対応: `E_INVALIDARG` を返します |
| `IS_ENUMSTRING` | 倍長整数 | -5 | 非対応: `E_INVALIDARG` を返します |

バージョン 2.0.3 以前では、`IS_PHRASELIST` から `IS_ENUMSTRING` の値が誤っていました（69 から 73）。

## ソースからのビルド

### 必要なもの

- Xcode（macOS）
- Visual Studio 2022、v143 ツールセット、Windows 10 SDK（Windows）

### クローン

```bash
git clone https://github.com/miyako/4d-plugin-input-scope.git
cd 4d-plugin-input-scope
```

### ビルド（macOS）

```bash
xcodebuild -project "Input Scope.xcodeproj" -target "Input Scope" -configuration Default ARCHS="arm64 x86_64" ONLY_ACTIVE_ARCH=NO CODE_SIGNING_ALLOWED=NO build
```

### ビルド（Windows）

```pwsh
msbuild "Input Scope.sln" /p:Configuration=Release /p:Platform=x64 /p:PlatformToolset=v143 /p:WindowsTargetPlatformVersion=10.0 /m
```

### テストの実行

プラグインはフォーカスのあるウインドウの IME を変更するため、Windows で手動テストします:

1. プラグインをビルドして `test/Plugins` にコピーします
2. 4D で `test/Project/test.4DProject` を開きます
3. `TEST` メソッドを実行し、フォームのフィールドをクリックしてから、ボタンをクリックして IME のモードを切り替えます

## CI/CD

このプロジェクトは手動実行のワークフローを 2 つ使います。詳しくは[ワークフローと復旧のガイド](.github/README.md)を参照してください。

| ワークフロー | トリガー | 目的 |
|---|---|---|
| `bump-version.yml` (**Bump version**) | 手動、任意のブランチ。入力は `patch`、`minor`、`major` | ソースのバージョンを上げてコミットします。ビルドやタグ付けはしません |
| `release.yml` (**Build**) | 手動、任意の ref。入力なし | Windows x64 と macOS universal をビルドし、署名・公証して `.zip` と `.dmg` のリリースを公開します |

既存のリリースタグは上書きされません。**Build** の前に **Bump version** を実行してください。

### 必要なシークレット（`release.yml` のみ）

**Settings → Secrets and variables → Actions** で設定します:

| シークレット | 説明 |
|---|---|
| `APPLE_DEVELOPER_ID_CERTIFICATE` | 秘密鍵を含む Developer ID Application `.p12` を Base64 エンコードしたもの |
| `APPLE_DEVELOPER_ID_CERTIFICATE_PASSWORD` | `.p12` 書き出し時のパスワード |
| `KEYCHAIN_PASSWORD` | CI ランナーの一時キーチェーン用の独立したパスワード |
| `NOTARYTOOL_APPLE_ID` | 公証に使う Apple ID のメールアドレス |
| `NOTARYTOOL_TEAM_ID` | Apple Developer の Team ID（英数字 10 文字） |
| `NOTARYTOOL_PASSWORD` | Apple のアプリ用パスワード（アカウントのパスワードではありません） |

## ライセンス

MIT。[LICENSE](LICENSE) を参照してください。

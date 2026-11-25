# ハングルドロップ公開サイト：セキュリティ自己監査結果

**実施日：2026年11月25日** ／ 対象：[`keides2/hangul-drop-site`](https://github.com/keides2/hangul-drop-site)（公開用 `main`）  
**現行ゲーム本体のGit blob SHA：** `8c520d9cf917f424d57ced4aee3e0aaeb0350ab6`（CSP初版：`3e938f0408bac927baa3ea5ecfb03955f6ba1ac4`）

**総合判断：自己監査では対象パターンに重大な異常は検出されませんでした。CSP導入後のZAP再診断では12種類の警告が残っています（導入前は13種類）。** 「安全認証済み」「脆弱性ゼロ」ではありません。**[独立した検査エンジンの実行結果・警告詳細](INDEPENDENT_SECURITY_CHECKS.md)** を併せて確認してください。

## 検査項目・測定値

| 分類 | 項目 | 観測結果 |
| --- | --- | --- |
| 公開コード | ゲーム本体 | HTML 1ファイル |
| 外部依存 | ゲーム中に読み込む外部JavaScript・CSS・画像 | **0件** |
| 通信処理 | `fetch` / XHR / WebSocket / EventSource / `sendBeacon` | **0件** |
| ブラウザー動作 | 試験した3画面・基本操作で観測した外部リクエスト | **0件** |
| ブラウザー動作 | 試験中のJavaScript実行例外 | **0件** |
| 認証情報 | 典型的なトークン・APIキー・秘密鍵のパターン | **0件** |
| 個人情報 | 公開ファイル中のメールアドレス形式 | **0件** |
| コード評価 | `eval` / `new Function` などの動的コード実行パターン | **0件** |
| DOM | `innerHTML` 等のHTML文字列挿入パターン | **0件** |
| 保存データ | `localStorage` | **最高得点の読込1箇所・書込1箇所** |
| 広告・解析 | アプリ内の広告SDK・アクセス解析SDK | **実装なし** |
| 配布履歴 | 公開リポジトリの初期コミット | **非公開開発履歴を含まない1件から開始** |
| メール保護 | 確認した公開Gitコミット | **GitHubの非公開用メールアドレス** |
| 公開処理 | GitHub Pagesデプロイ | **成功実行履歴を確認** |

上記のソースコード検査は **`tests/security_audit.py`** に基づくパターン検査です。対象ファイルやパターンに依存するため、網羅的な脆弱性診断ではありません。

## ブラウザーでの実行確認

Chromium + Playwrightを使い、公開版と同じ内容の `index.html` をローカルで実行しました。検査画面は **390×844、360×640、844×390** の3種類です。

ゲーム開始、左右移動、一気に落下、NEXTスキップ、効果音のON/OFFを操作し、試験中のブラウザー例外0件、観測した外部ネットワーク要求0件を確認しました。

**注意：** ローカルHTMLのブラウザー試験であり、本番のGitHub Pagesサーバーとの通信内容やセキュリティヘッダーを測定した結果ではありません。音声合成エンジンの内部通信も対象外です。

## プライバシーの範囲

- アカウント登録、アプリ独自のサーバー送信、広告、アクセス解析は、現行ゲーム本体にはありません。
- 保存するのは最高得点のみで、ブラウザーのサイトデータ削除によって消去できます。
- **GitHub Pages側ではアクセスしたIPアドレスなどが記録され得ます。** これはゲームのJavaScriptが外部送信するかとは別の話です。
- 韓国語読み上げはブラウザー／端末の音声合成機能を使用します。OSや音声エンジン側の処理はこの監査の対象外です。
- 初期公開時の非公開開発リポジトリのコミット履歴は移植していません。**今回のREADME・監査追加コミットにもGitHubアカウントの表示名が履歴として記録されています**。コミットのメールアドレスはGitHubの非公開用形式ですが、表示名まで匿名化されるわけではありません。表示名を秘匿するにはGit履歴の再作成が必要で、READMEの修正だけでは消せません。

## 未検証事項・残るリスク

1. **専門家による第三者監査・ペネトレーションテストは未実施。** CodeQL・ZAPによる自動診断を実施しましたが、既知パターンに該当しない脆弱性を否定できません。
2. **本番HTTPヘッダーはZAP 2.17.0で測定済み。** [外部検査結果](INDEPENDENT_SECURITY_CHECKS.md)のとおり、CSP、クリックジャッキング対策、`X-Content-Type-Options`などの警告があります。TLS証明書の詳細やMozilla Observatoryの点数は未測定です。
3. **CSPはHTMLのmetaで適用済み。** インラインJavaScript／CSSを正確なSHA-256ハッシュで許可し、それ以外のスクリプトや外部通信等は拒否します。Chromiumの3画面と不正スクリプト・CSS・通信の否定試験を通過しました。**HTTPレスポンスヘッダーとしてのCSPは設定されておらず、`frame-ancestors` はmetaでは使用できません。** GitHub Pages側の制約が残ります。
4. **通信0件はテストした操作・環境での観測値。** すべての端末・音声エンジン・操作経路の結果ではありません。
5. **GitHubのシークレットスキャン警告一覧やリポジトリ設定は未照会。** 管理画面での確認を推奨します。
6. CSP適用後のZAP再検査は**FAIL 0 / WARN 12種類 / PASS 56**（導入前はFAIL 0 / WARN 13種類 / PASS 55）です（[原本リンク・内容の解説](INDEPENDENT_SECURITY_CHECKS.md)）。CodeQLの実行は成功し、HTML 1件の解析もログで確認しましたが、CodeQLの警告件数は未確認です。
7. **字母の空き部分への配置を認識する変更**ではCSPハッシュも再計算済みです。ブラウザーの組字・パッチム保持・消去試験と10種類の位置判定テストを追加しました。新しい公開HTMLのZAP再検査も **PASS 56 / WARN 12種類 / FAIL 0**（[実行原本](https://github.com/keides2/hangul-drop-site/actions/runs/45569372823)）です。
8. 検査結果は**この版・この時点**のものです。更新後は再実行してください。

## 再現手順・継続チェック

Python標準ライブラリだけで静的検査できます。

```bash
python3 tests/security_audit.py
python3 tools/csp_hashes.py --check
```

ブラウザーテスト（任意、Playwright + Chromiumが必要）：

```bash
python -m pip install playwright
python -m playwright install chromium
python tests/browser_security_smoke.py
python tests/csp_browser_smoke.py
```

GitHub Actionsの **[Public site security checks](https://github.com/keides2/hangul-drop-site/actions/workflows/security-audit.yml)** は`main`へのpushやプルリクエストのたびに静的検査を再実行します。加えて、[CodeQL](https://github.com/keides2/hangul-drop-site/actions/workflows/codeql.yml) と [ZAP](https://github.com/keides2/hangul-drop-site/actions/workflows/zap-baseline.yml) の検査も利用できます。**緑色の実行結果だけで警告0件とは判断しないでください。**

## 参考（GitHub公式・公開情報）

- [GitHub Pages：HTTPSによる公開](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
- [GitHub Pages：アクセス時のIPアドレスのログ](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [GitHub：Secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning)
- [GitHub Community：PagesでのカスタムHTTPヘッダーの制約](https://github.com/orgs/community/discussions/54257)

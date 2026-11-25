# 外部検査ツールによるセキュリティ評価（2026年11月25日）

**対象サイト：** <https://keides2.github.io/hangul-drop-site/>  
**公開ソース：** [index.html](index.html)（Git blob `66e7ae55ec88fd859373c4a8e46b59fccc3bf1bc`）

> **判定：公開サイトは稼働し、今回の外部スキャンでFAIL判定は0件でした。ただし13種類の警告があり、「脆弱性なし」「安全認証済み」ではありません。**
>
> 本文は検査結果の読み解きです。自己申告の要約だけでなく、下記のGitHub Actionsの**元の実行ログ・ZAP生成レポート**を参照してください。

## 独立した検査エンジンの実行記録

| エンジン | 対象・結果 | 検証可能な原本 |
| --- | --- | --- |
| **GitHub CodeQL**（静的解析） | 実行成功。ログで **HTML 1/1ファイルを解析**したことを確認。**検出アラート件数は本書では未確認** | [CodeQL実行ログ](https://github.com/keides2/hangul-drop-site/actions/runs/45541532793) / [Security → Code scanning](https://github.com/keides2/hangul-drop-site/security/code-scanning) |
| **ZAP 2.17.0 Baseline**（稼働サイトへのパッシブ診断） | **PASS 55 / WARN 13種類 / FAIL 0**。ワークフロー自体は成功しましたが、警告0件という意味ではありません | [ZAP実行ログと生成レポート（ZIP）](https://github.com/keides2/hangul-drop-site/actions/runs/45541647370) |
| **独自静的チェック**（補助的な自己検査） | PASS。外部通信API、秘密情報の既知パターン等を検査 | [実行ログ](https://github.com/keides2/hangul-drop-site/actions/runs/45541647468) / [検査コード](tests/security_audit.py) |

ZAPの測定日時は **2026-11-25 03:41 UTC（日本時間12:41）**。ZAPレポートには **ゲームURLへのHTTP 200 OK** が記録されています。ZAPは一部でホストのルート `https://keides2.github.io/`、`robots.txt`、`sitemap.xml` も検査し、そこは404でした。**ルート404の指摘をゲーム画面の指摘と混同しない**ようにしてください。

## ZAPの主な警告とリスク評価

| 警告（ZAP ID） | 対象 | ZAPのリスク | 解釈・対応 |
| --- | --- | --- | --- |
| Content Security Policyヘッダーなし（10038） | ゲームの200応答 | **Medium** | XSSを防ぐ多層防御が弱い。**改善優先候補**。インラインJSを維持する場合は適切なCSPハッシュなどを検討 |
| 埋め込み防止ヘッダーなし（10020） | ゲームの200応答 | **Medium** | 他サイトからiframeで表示できる可能性。**ログイン・送金・個人情報入力がない**現行ゲームの実被害リスクは比較的小さいが、対策候補 |
| `Access-Control-Allow-Origin: *`（10098） | ゲームの200応答 | **Medium** | 公開HTMLを誰でも読み取れる設定。公開専用の機密情報なしHTMLでは、これ自体で秘密情報が漏れるわけではない。非公開情報を同一ホストへ置かないこと |
| `X-Content-Type-Options` なし（10021） | ゲームの200応答 | **Low** | MIMEスニッフィング抑制用ヘッダーがない。GitHub Pagesの配信ヘッダーの制約とともに検討 |
| COOP・COEP ヘッダー不足（90004） | ゲームの200応答 | **Low** | オリジン間分離の追加防御が未設定 |
| HSTS・Permissions Policy、CSP補助ディレクティブなど | **主にホストの404応答** | Low / Medium | GitHub Pagesの共有ホスティング設定・ルート404に由来するものを含む。ゲーム単独の脆弱性とは区別 |
| JavaScriptコメント、キャッシュ可能な公開コンテンツなど | 主に公開応答 | Informational | 通常の静的ゲームでは必ずしも脆弱性ではない。コメント中に機密情報がないかは別途確認 |

**重要：** ZAPのMediumは検査ルールの一般的な分類です。実際に攻撃できることが確認された、という意味ではありません。逆に、ゼロ件のFAILでも完全に安全とは証明できません。

**現在確認できていないこと：** アクティブな侵入テスト、全ブラウザー・端末の安全性、GitHubアカウントの保護状況、Google Safe Browsingの最新サイト判定、Mozilla Observatoryの実測点数、CodeQLアラート一覧の件数。

## 利用者に関係する脅威を整理

| 利用者の懸念 | 現行コードについて確認できたこと | 残るリスク |
| --- | --- | --- |
| 氏名・メール・入力情報の流出 | ゲームに入力フォーム・登録機能なし。外部送信API・広告SDK・解析SDKなし | GitHub Pagesのアクセスログ・音声合成エンジンの処理は別。公開Git履歴の作者表示名は見える |
| 悪意あるスクリプトの実行 | 外部JS依存なし、`eval` / `innerHTML` 系の危険パターンを確認した範囲では使用せず、表示更新は主に `textContent` | CSPヘッダーが未設定。将来のコード変更・アカウント乗っ取り・ホスト側の問題は残る |
| サイトを開いたら端末を操作される | 現行コードに外部送信・端末権限の要求なし | ブラウザー自体や端末の未知の脆弱性までは検証できない |
| 外部サービスへの依存 | JavaScript/CSS/画像の外部ロードなし | GitHub Pagesとブラウザーの音声合成に依存 |
| 最高得点データ | `localStorage` のキーは `jamo-drop-syllableclear-best` の1つ | 同一オリジン `keides2.github.io` 内の**他のパス上のページとはストレージ領域を共有**するため、重要な個人データは保存しない |

## 利用者自身が利用できる外部評価

これらは**公的機関の「安全認証」ではありません**。提供元の異なる外部検査で、評価対象も異なります。

- **[Mozilla / MDN HTTP Observatory](https://developer.mozilla.org/en-US/observatory/analyze?host=keides2.github.io)**：HTTPセキュリティヘッダー等の設定に点数・ランクを付ける。対象は主にホスト `keides2.github.io`。**今回の実測ランクは未取得**。
- **[Google Safe Browsing サイトステータス](https://transparencyreport.google.com/safe-browsing/search?url=https%3A%2F%2Fkeides2.github.io%2Fhangul-drop-site%2F)**：Googleが把握するフィッシング・マルウェア等の危険サイト判定。**今回の個別判定は未取得**。「危険と判定されていない」ことは完全な安全の証明ではない。
- **[Qualys SSL Labs](https://www.ssllabs.com/ssltest/analyze.html?d=keides2.github.io)**：TLS暗号化・証明書・HTTPS構成。主にGitHub Pages側のホストを評価する。**今回の実測ランクは未取得**。
- **[IPA「安全なウェブサイトの作り方」](https://www.ipa.go.jp/security/vuln/websecurity/)**：公的機関のWebセキュリティ対策指針。**個別サイトの認証や安全点数は発行しない**。
- **[NIST National Vulnerability Database](https://nvd.nist.gov/)** と **[CVSS](https://www.first.org/cvss/)**：公表された脆弱性と**発見された個別脆弱性の深刻度**に関する情報。未登録なら安全という意味ではなく、サイト全体の安全スコアでもない。

### 次の改善候補

1. **CSP導入**：ページ内のJavaScript・CSSに適合するポリシーを設計し、ブラウザー実動作への影響を確認する。
2. **クリックジャッキング対策**：フレーム埋め込みの要否を決める。GitHub Pagesが配信するHTTPヘッダーに設定制限がある場合、適切なホスト変更を検討する。
3. **継続検査**：CodeQLの警告一覧とZAPのレポートを定期的に確認し、警告を新しいリリースの合否判定に適切に反映させる。

最終更新：2026-11-25。**この結果は本報告書作成時点の観測値に限定されます。**

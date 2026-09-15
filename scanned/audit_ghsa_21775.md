# [H] Validation bypass in frourio

## Summary
Severity: High
Advisory: GHSA-8xxm-h73r-ghfj
CVE: CVE-2022-23623
CWE: CWE-1321, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-07
Source: https://github.com/advisories/GHSA-8xxm-h73r-ghfj
Type: github-advisory

## Affected
- npm: `frourio` — affected >=0 <0.26.0

## Details
## 日本語

### 影響
v0.26.0以前のfrourioを使用している、かつvalidators/を利用している場合、ネストされたバリデータがリクエストのボディーとクエリに対して正しく働かないケースがあります。また、リクエストに対してバリデーションが効かなくなる入力があります。

### パッチ
frourioをv0.26.0かそれ以降のバージョンにアップデートをお願いします。frourio を使用したプロジェクトには `class-transformer` と `reflect-metadata` の依存への追加も必要となります。

### ワークアラウンド
controller側で自分でclass-transformerを使用してチェックする、vaildatorを使わない、など。

### さらなる情報

このセキュリティ勧告に関する質問やコメントについては、以下の方法でお問い合わせいただけます。
* [frourio](https://github.com/frouriojs/frourio)にIssueを開く。

## English

### Impact
Frourio users who uses frourio version prior to v0.26.0 and integration with class-validator through `validators/` folder. Validators does not work properly for request bodies and queries in specific situations. Addtionally, some kind of input is not validated. (false positives)

### Patches
Please update your frourio to v0.26.0 or later. You also need to install `class-transformer` and `reflect-metadata` to your project.

### Workarounds
Validate objects from request with class-transformer in controllers by yourself, or prevent using validators.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [frourio](https://github.com/frouriojs/frourio)

## References
- https://github.com/frouriojs/frourio/security/advisories/GHSA-8xxm-h73r-ghfj
- https://nvd.nist.gov/vuln/detail/CVE-2022-23623
- https://github.com/frouriojs/frourio/commit/7c19ac5363305b81b1c6b5232620228763d427af
- https://github.com/frouriojs/frourio

# [H] Yii 2: Local file inclusion via view parameter name collision

## Summary
Severity: High
Advisory: GHSA-5vpg-rj7q-qpw2
CVE: CVE-2026-39850
CWE: CWE-20, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-5vpg-rj7q-qpw2
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=0 <2.0.55

## Details
The core view rendering method `View::renderPhpFile()` calls `extract($_params_, EXTR_OVERWRITE)` before the `require` statement that includes the view file. A caller-controlled parameter named `_file_` in the `$params` array overwrites the internal local variable that specifies which file is included — enabling a Local File Inclusion primitive.

### Impact

- Local File Inclusion (arbitrary file read via non-PHP files)
- Potential RCE if attacker can write PHP files via a separate primitive
- Information disclosure

### Patches

2.0.55

### Workarounds

No.

## References
- https://github.com/yiisoft/yii2/security/advisories/GHSA-5vpg-rj7q-qpw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39850
- https://github.com/yiisoft/yii2/commit/109878b491dbffa541032bc99fb5e26d12cd0375
- https://github.com/yiisoft/yii2
- https://github.com/yiisoft/yii2/releases/tag/2.0.55

# [C] XpressEngine vulnerable to Unrestricted Upload of File with Dangerous Type

## Summary
Severity: Critical
Advisory: GHSA-8r5j-22j5-w4cm
CVE: CVE-2021-26642
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-8r5j-22j5-w4cm
Type: github-advisory

## Affected
- Packagist: `xpressengine/xpressengine` — affected >=0 <3.0.15

## Details
When uploading an image file to a bulletin board developed with XpressEngine, a vulnerability in which an arbitrary file can be uploaded due to insufficient verification of the file. A remote attacker can use this vulnerability to execute arbitrary code on the server where the bulletin board is running.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26642
- https://github.com/xpressengine/xpressengine/issues/1366
- https://boho.or.kr/krcert/secNoticeView.do?bulletin_writing_sequence=67125

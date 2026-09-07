# [H] Subrion CMS RCE Vulnerability

## Summary
Severity: High
Advisory: GHSA-73xj-v6gc-g5p5
CVE: CVE-2018-19422
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-73xj-v6gc-g5p5
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0 <4.2.2

## Details
`/panel/uploads` in Subrion CMS 4.2.1 allows remote attackers to execute arbitrary PHP code via a .pht or .phar file, because the .htaccess file omits these.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19422
- https://github.com/intelliants/subrion/issues/801
- https://github.com/intelliants/subrion/commit/74359bcfaea424edda6d782a8ac25397c55972ab
- http://packetstormsecurity.com/files/162591/Subrion-CMS-4.2.1-Shell-Upload.html
- http://packetstormsecurity.com/files/173998/Intelliants-Subrion-CMS-4.2.1-Remote-Code-Execution.html

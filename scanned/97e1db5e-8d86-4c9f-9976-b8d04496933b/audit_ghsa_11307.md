# [H] Concrete CMS vulnerable to Remote Code Execution by stored PHP object injection

## Summary
Severity: High
Advisory: GHSA-gj26-w59c-29mf
CVE: CVE-2026-3452
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-gj26-w59c-29mf
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.4.8

## Details
Concrete CMS below version 9.4.8 is vulnerable to Remote Code Execution by stored PHP object injection into the Express Entry List block via the columns parameter. An authenticated administrator can store attacker-controlled serialized data in block configuration fields that are later passed to unserialize() without class restrictions or integrity checks. 

The Concrete CMS security team thanks YJK ( @YJK0805 https://hackerone.com/yjk0805 ) of  ZUSO ART https://zuso.ai/  for reporting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3452
- https://github.com/concretecms/concretecms/pull/12826/changes/167f16e4805d8ab546d2997c753ac21bf4854920
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/948-release-notes
- https://github.com/concretecms/concretecms

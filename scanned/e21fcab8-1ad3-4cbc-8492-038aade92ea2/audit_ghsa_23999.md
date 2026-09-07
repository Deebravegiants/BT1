# [H] OpenCart Path Traversal

## Summary
Severity: High
Advisory: GHSA-wx3q-f5f2-4q8v
CVE: CVE-2018-11494
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wx3q-f5f2-4q8v
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=0

## Details
The "program extension upload" feature in OpenCart through 3.0.2.0 has a six-step process (upload, install, unzip, move, xml, remove) that allows attackers to execute arbitrary code if the remove step is skipped, because the attacker can discover a secret temporary directory name (containing 10 random digits) via a directory traversal attack involving language_info['code'].

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11494
- https://github.com/opencart/opencart
- http://www.bigdiao.cc/2018/05/24/Opencart-v3-0-2-0

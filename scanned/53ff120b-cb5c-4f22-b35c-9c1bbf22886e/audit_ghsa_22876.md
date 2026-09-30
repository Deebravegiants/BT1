# [M] Subrion CMS PHP Object Injection

## Summary
Severity: Medium
Advisory: GHSA-fmqq-hw9m-448q
CVE: CVE-2020-12469
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fmqq-hw9m-448q
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
admin/blocks.php in Subrion CMS through 4.2.1 allows PHP Object Injection (with resultant file deletion) via serialized data in the subpages value within a block to blocks/edit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12469
- https://belong2yourself.github.io/vulnerabilities/docs/Subrion%20CMS/Insecure%20Deserialization/Subpages%20-%20Authenticated%20PHP%20Object%20Injection/readme
- https://github.com/belong2yourself/vulnerabilities/tree/master/Subrion%20CMS/Insecure%20Deserialization/Subpages%20-%20Authenticated%20PHP%20Object%20Injection
- https://github.com/intelliants/subrion

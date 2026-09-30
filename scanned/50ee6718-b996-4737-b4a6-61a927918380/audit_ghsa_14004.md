# [M] Pimcore Path Traversal Vulnerability in AdminBundle/Controller/Reports/CustomReportController.php

## Summary
Severity: Medium
Advisory: GHSA-g2mc-fqqc-hxg3
CVE: CVE-2023-30855
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-02
Source: https://github.com/advisories/GHSA-g2mc-fqqc-hxg3
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.18

## Details
### Impact
The impact of this path traversal and arbitrary extension is limited (creation of arbitrary files and appending data to existing files) but when combined with the SQL Injection, the exported data `RESTRICTED DIFFUSION 9 / 9` can be controlled and a webshell can be uploaded. Attackers can use that to execute arbitrary PHP code on the server with the permissions of the webserver.

### Patches
Update to version 10.5.18 or apply this patch manually https://github.com/pimcore/pimcore/commit/7f788fa44bc18bc1c9182c25e26b770a1d30b62f.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/7f788fa44bc18bc1c9182c25e26b770a1d30b62f.patch manually.


### References
https://github.com/pimcore/pimcore/pull/14498

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-g2mc-fqqc-hxg3
- https://nvd.nist.gov/vuln/detail/CVE-2023-30855
- https://github.com/pimcore/pimcore/pull/14498
- https://github.com/pimcore/pimcore/commit/7f788fa44bc18bc1c9182c25e26b770a1d30b62f.patch
- https://github.com/pimcore/pimcore/commit/f1d904094700b513c4756904fa2b1e19d08d890e.patch
- https://github.com/pimcore/pimcore

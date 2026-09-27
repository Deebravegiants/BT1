# [C] Snuffleupagus vulnerable to RCE on instances with upload validation enabled but without the VLD package

## Summary
Severity: Critical
Advisory: CVE-2026-22034
Aliases: GHSA-c4ch-xw5p-2mvc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-22034
Type: osv

## Details
Snuffleupagus is a module that raises the cost of attacks against website by killing bug classes and providing a virtual patching system. On deployments of Snuffleupagus prior to version 0.13.0 with the non-default upload validation feature enabled and configured to use one of the upstream validation scripts based on Vulcan Logic Disassembler (VLD) while the VLD extension is not available to the CLI SAPI, all files from multipart POST requests are evaluated as PHP code. The issue was fixed in version 0.13.0.

## References
- https://github.com/jvoisin/snuffleupagus/blob/9278dc77bab2a219e770a1b31dd6797bc9070e37/src/sp_upload_validation.c#L92-L100
- https://github.com/jvoisin/snuffleupagus/blob/v0.12.0/scripts/upload_validation.php
- https://github.com/jvoisin/snuffleupagus/blob/v0.12.0/scripts/upload_validation.py
- https://github.com/php/php-src/blob/e4098da58a9eaee759d728d98a27d809cde37671/ext/standard/dl.c#L165-L166
- https://github.com/php/php-src/blob/e4098da58a9eaee759d728d98a27d809cde37671/main/rfc1867.c#L1269-L1274
- https://snuffleupagus.readthedocs.io/config.html#upload-validation
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22034.json
- https://github.com/jvoisin/snuffleupagus/security/advisories/GHSA-c4ch-xw5p-2mvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-22034
- https://github.com/jvoisin/snuffleupagus/commit/9278dc77bab2a219e770a1b31dd6797bc9070e37

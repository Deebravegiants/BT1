# [H] Cacti RCE vulnerability by file include in lib/plugin.php

## Summary
Severity: High
Advisory: CVE-2024-31459
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-31459
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. Prior to version 1.2.27, there is a file inclusion issue in the `lib/plugin.php` file. Combined with SQL injection vulnerabilities, remote code execution can be implemented. There is a file inclusion issue with the `api_plugin_hook()` function in the `lib/plugin.php` file, which reads the plugin_hooks and plugin_config tables in database. The read data is directly used to concatenate the file path which is used for file inclusion. Version 1.2.27 contains a patch for the issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31459.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-cx8g-hvq8-p2rv
- https://github.com/Cacti/cacti/security/advisories/GHSA-gj3f-p326-gh8r
- https://github.com/Cacti/cacti/security/advisories/GHSA-pfh9-gwm6-86vp
- https://nvd.nist.gov/vuln/detail/CVE-2024-31459

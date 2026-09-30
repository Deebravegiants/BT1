# [H] Apache Allura: sensitive information exposure via DNS rebinding

## Summary
Severity: High
Advisory: CVE-2024-36471
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-10
Source: https://osv.dev/vulnerability/CVE-2024-36471
Type: osv

## Details
Import functionality is vulnerable to DNS rebinding attacks between verification and processing of the URL.  Project administrators can run these imports, which could cause Allura to read from internal services and expose them.

This issue affects Apache Allura from 1.0.1 through 1.16.0.

Users are recommended to upgrade to version 1.17.0, which fixes the issue.  If you are unable to upgrade, set "disable_entry_points.allura.importers = forge-tracker, forge-discussion" in your .ini config file.

## References
- http://www.openwall.com/lists/oss-security/2024/06/10/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36471.json
- https://lists.apache.org/thread/g43164t4bcp0tjwt4opxyks4svm8kvbh
- https://nvd.nist.gov/vuln/detail/CVE-2024-36471

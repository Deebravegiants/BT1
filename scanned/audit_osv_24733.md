# [H] Roxy-WI vulnerable to Limited Path Traversal in name parameter

## Summary
Severity: High
Advisory: CVE-2023-25804
Aliases: GHSA-69j6-crq8-rrhv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-25804
Type: osv

## Details
Roxy-WI is a Web interface for managing Haproxy, Nginx, Apache, and Keepalived servers. Versions prior to 6.3.5.0 have a limited path traversal vulnerability. An SSH key can be saved into an unintended location, for example the `/tmp` folder using a payload `../../../../../tmp/test111_dev`. This issue has been fixed in version 6.3.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25804.json
- https://github.com/hap-wi/roxy-wi/security/advisories/GHSA-69j6-crq8-rrhv
- https://nvd.nist.gov/vuln/detail/CVE-2023-25804

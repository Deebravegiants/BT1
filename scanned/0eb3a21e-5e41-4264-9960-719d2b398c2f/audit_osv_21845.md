# [H] Authenticated Remote Code Execution in OpenLiteSpeed Web Server

## Summary
Severity: High
Advisory: CVE-2022-0073
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-27
Source: https://osv.dev/vulnerability/CVE-2022-0073
Type: osv

## Details
Improper Input Validation vulnerability in LiteSpeed Technologies OpenLiteSpeed Web Server and LiteSpeed Web Server dashboards allows Command Injection. This affects 1.7.0  versions before 1.7.16.1.

## References
- https://github.com/litespeedtech/openlitespeed/blob/v1.7.16.1/dist/admin/html.open/lib/CValidation.php#L565
- https://github.com/litespeedtech/openlitespeed/blob/v1.7.16/dist/admin/html.open/lib/CValidation.php#L565
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0073.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-0073
- https://github.com/litespeedtech/openlitespeed

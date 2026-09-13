# [C] CVE-2024-45509

## Summary
Severity: Critical
Advisory: CVE-2024-45509
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-01
Source: https://osv.dev/vulnerability/CVE-2024-45509
Type: osv

## Details
In MISP through 2.4.196, app/Controller/BookmarksController.php does not properly restrict access to bookmarks data in the case where the user is not an org admin.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45509.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45509
- https://github.com/MISP/MISP/commit/3f3b9a574f349182a545636e12efa39267e9db04

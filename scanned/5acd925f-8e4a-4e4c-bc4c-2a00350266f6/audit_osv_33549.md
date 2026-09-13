# [H] CVE-2025-46099

## Summary
Severity: High
Advisory: CVE-2025-46099
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-07-23
Source: https://osv.dev/vulnerability/CVE-2025-46099
Type: osv

## Details
In Pluck CMS 4.7.20-dev, an authenticated attacker can upload or create a crafted PHP file under the albums module directory and access it via the module routing logic in albums.site.php, resulting in arbitrary command execution through a GET parameter.

## References
- https://github.com/0xC4J/CVE-Lists/blob/main/CVE-2025-46099/CVE-2025-46099.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46099.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46099

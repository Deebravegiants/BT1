# [C] CVE-2024-29858

## Summary
Severity: Critical
Advisory: CVE-2024-29858
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-29858
Type: osv

## Details
In MISP before 2.4.187, __uploadLogo in app/Controller/OrganisationsController.php does not properly check for a valid logo upload.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29858.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29858
- https://github.com/MISP/MISP/commit/6a2986be6aad6b37858b4869e238f517b295c111

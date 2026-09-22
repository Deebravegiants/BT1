# [M] CVE-2024-34191

## Summary
Severity: Medium
Advisory: CVE-2024-34191
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/CVE-2024-34191
Type: osv

## Details
htmly v2.9.6 was discovered to contain an arbitrary file deletion vulnerability via the delete_post() function at admin.php. This vulnerability allows attackers to delete arbitrary files via a crafted request.

## References
- https://chmod744.super.site/htmly-cve
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34191.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34191

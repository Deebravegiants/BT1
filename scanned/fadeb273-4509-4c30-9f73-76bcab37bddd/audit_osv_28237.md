# [C] CVE-2024-29859

## Summary
Severity: Critical
Advisory: CVE-2024-29859
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-29859
Type: osv

## Details
In MISP before 2.4.187, add_misp_export in app/Controller/EventsController.php does not properly check for a valid file upload.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29859.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29859
- https://github.com/MISP/MISP/commit/238010bfd004680757b324cba0c6344f77a25399

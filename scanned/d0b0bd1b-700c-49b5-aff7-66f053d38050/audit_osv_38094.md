# [M] PdfDing: Shared PDF Expiration, Max Views, and Deletion Bypass via Serve/Download Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-34586
Aliases: GHSA-vfqx-2464-38wf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34586
Type: osv

## Details
PdfDing is a selfhosted PDF manager, viewer and editor offering a seamless user experience on multiple devices. Prior to version 1.7.1, check_shared_access_allowed() validates only session existence — it does not check SharedPdf.inactive (expiration / max views) or SharedPdf.deleted. The Serve and Download endpoints rely solely on this function, allowing previously-authorized users to access shared PDF content after expiration, view limit, or soft-deletion. This issue has been patched in version 1.7.1.

## References
- https://github.com/mrmn2/PdfDing/releases/tag/v1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34586.json
- https://github.com/mrmn2/PdfDing/security/advisories/GHSA-vfqx-2464-38wf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34586
- https://github.com/mrmn2/PdfDing/commit/a6783b259b25c839c52c6f2380333827a52e89eb

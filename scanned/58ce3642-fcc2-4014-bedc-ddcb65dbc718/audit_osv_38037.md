# [H] PdfDing: Password-protected share bypass via direct serve endpoint

## Summary
Severity: High
Advisory: CVE-2026-34376
Aliases: GHSA-42x7-vvj4-4cj3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34376
Type: osv

## Details
PdfDing is a selfhosted PDF manager, viewer and editor offering a seamless user experience on multiple devices. Prior to version 1.7.0, an access-control vulnerability allows unauthenticated users to retrieve password-protected shared PDFs by directly calling the file-serving endpoint without completing the password verification flow. This results in unauthorized access to confidential documents that users expected to be protected by a shared-link password. This issue has been patched in version 1.7.0.

## References
- https://github.com/mrmn2/PdfDing/releases/tag/v1.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34376.json
- https://github.com/mrmn2/PdfDing/security/advisories/GHSA-42x7-vvj4-4cj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34376
- https://github.com/mrmn2/PdfDing/commit/ae579ea98c5603d1435e0d90e81d72151564088a
- https://github.com/mrmn2/PdfDing/pull/294

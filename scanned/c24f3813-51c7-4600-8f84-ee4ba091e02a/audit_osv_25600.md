# [C] Improper Authentication in PrivateUploader

## Summary
Severity: Critical
Advisory: CVE-2023-40020
Aliases: GHSA-vhrw-2472-rrjx
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2023-08-14
Source: https://osv.dev/vulnerability/CVE-2023-40020
Type: osv

## Details
PrivateUploader is an open source image hosting server written in Vue and TypeScript. In affected versions `app/routes/v3/admin.controller.ts` did not correctly verify whether the user was an administrator (High Level) or moderator (Low Level) causing the request to continue processing. The response would be a 403 with ADMIN_ONLY, however, next() would call leading to any updates/changes in the route to process. This issue has been addressed in version 3.2.49. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40020.json
- https://github.com/PrivateUploader/PrivateUploader/security/advisories/GHSA-vhrw-2472-rrjx
- https://nvd.nist.gov/vuln/detail/CVE-2023-40020
- https://github.com/PrivateUploader/PrivateUploader/commit/869657d61e3c7a518177106fe63ea483082b0d3e

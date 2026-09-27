# [H] Unauthenticated File Upload in parisneo/lollms

## Summary
Severity: High
Advisory: CVE-2026-0558
Aliases: PYSEC-2026-2198
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-29
Source: https://osv.dev/vulnerability/CVE-2026-0558
Type: osv

## Details
A vulnerability in parisneo/lollms, up to and including version 2.2.0, allows unauthenticated users to upload and process files through the `/api/files/extract-text` endpoint. This endpoint does not enforce authentication, unlike other file-related endpoints, and lacks the `Depends(get_current_active_user)` dependency. This issue can lead to denial of service (DoS) through resource exhaustion, information disclosure, and violation of the application's documented security policies.

## References
- https://huntr.com/bounties/0a722001-89ce-4c91-b6a6-a55ee5ba2113
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0558.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0558
- https://github.com/parisneo/lollms/commit/a6625dc83786ff21d109b0d545ca61b770607ef3

# [H] CVE-2025-59305

## Summary
Severity: High
Advisory: CVE-2025-59305
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-59305
Type: osv

## Details
Improper authorization in the background migration endpoints of Langfuse 3.1 before d67b317 allows any authenticated user to invoke migration control functions. This can lead to data corruption or denial of service through unauthorized access to TRPC endpoints such as backgroundMigrations.all, backgroundMigrations.status, and backgroundMigrations.retry.

## References
- https://depthfirst.com/post/how-an-authorization-flaw-reveals-a-common-security-blind-spot-cve-2025-59305-case-study
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59305.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59305

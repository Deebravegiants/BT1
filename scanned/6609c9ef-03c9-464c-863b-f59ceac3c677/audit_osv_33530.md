# [M] CVE-2025-45731

## Summary
Severity: Medium
Advisory: CVE-2025-45731
Aliases: GHSA-ph6w-q992-7qrx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-07-24
Source: https://osv.dev/vulnerability/CVE-2025-45731
Type: osv

## Details
A group deletion race condition in 2FAuth v5.5.0 causes data inconsistencies and orphaned accounts when a group is deleted while other operations are pending.

## References
- https://github.com/Bubka/2FAuth/security/advisories/GHSA-ph6w-q992-7qrx
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/45xxx/CVE-2025-45731.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-45731
- https://github.com/Bubka/2FAuth/commit/b82a7eb604ddfe994fadce7db3a9e4a201c54a83

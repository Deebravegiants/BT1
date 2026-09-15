# [M] CVE-2025-46011

## Summary
Severity: Medium
Advisory: CVE-2025-46011
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-06-04
Source: https://osv.dev/vulnerability/CVE-2025-46011
Type: osv

## Details
Listmonk v4.1.0 (fixed in v5.0.0) is vulnerable to SQL Injection in the QuerySubscribers function which allows attackers to escalate privileges.

## References
- https://github.com/kevinroleke/security/tree/main/CVE-2025-46011
- https://github.com/knadh/listmonk/releases/tag/v4.1.0
- https://github.com/knadh/listmonk/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46011.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46011
- https://github.com/knadh/listmonk/issues/2412
- https://github.com/knadh/listmonk/commit/4b805f885b9f5a20126ec06f8b59dc448c4af33b

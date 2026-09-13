# [C] Manager-io/Manager allows unauthenticated full read server-side request forgery in "proxy" endpoint

## Summary
Severity: Critical
Advisory: CVE-2025-54122
Aliases: GHSA-347w-cgwh-m895
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-21
Source: https://osv.dev/vulnerability/CVE-2025-54122
Type: osv

## Details
Manager-io/Manager is accounting software. A critical unauthenticated full read Server-Side Request Forgery (SSRF) vulnerability has been identified in the proxy handler component of both manager Desktop and Server edition versions up to and including 25.7.18.2519. This vulnerability allows an unauthenticated attacker to bypass network isolation and access restrictions, potentially enabling access to internal services, cloud metadata endpoints, and exfiltration of sensitive data from isolated network segments. This vulnerability is fixed in version 25.7.21.2525.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54122.json
- https://github.com/Manager-io/Manager/security/advisories/GHSA-347w-cgwh-m895
- https://nvd.nist.gov/vuln/detail/CVE-2025-54122

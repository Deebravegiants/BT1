# [H] Parse Server has a bypass of class-level permissions in LiveQuery

## Summary
Severity: High
Advisory: GHSA-7ch5-98q2-7289
CVE: CVE-2026-30947
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-7ch5-98q2-7289
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.2-alpha.3
- npm: `parse-server` — affected >=0 <8.6.16

## Details
### Impact

Class-level permissions (CLP) are not enforced for LiveQuery subscriptions. An unauthenticated or unauthorized client can subscribe to any LiveQuery-enabled class and receive real-time events for all objects, regardless of CLP restrictions.

All Parse Server deployments that use LiveQuery with class-level permissions are affected. Data intended to be restricted by CLP is leaked to unauthorized subscribers in real time.

### Patches

The fix enforces CLP before creating the subscription and during event delivery.

### Workarounds

Disable LiveQuery for classes that use CLP restrictions by removing them from the `liveQuery.classNames` server configuration.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-7ch5-98q2-7289
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.3
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.16

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-7ch5-98q2-7289
- https://nvd.nist.gov/vuln/detail/CVE-2026-30947
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.16
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.3

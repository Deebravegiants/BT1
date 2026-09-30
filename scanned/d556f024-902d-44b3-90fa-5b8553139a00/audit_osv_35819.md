# [M] CVE-2026-15076

## Summary
Severity: Medium
Advisory: CVE-2026-15076
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-15076
Type: osv

## Details
In versions up to and including 4.5.29 (4.x branch) and 5.1.4 (5.x branch), the WebClientSession component of Eclipse Vert.x Web Client does not validate that the Domain attribute of a Set-Cookie response header matches the originating server's domain, in violation of RFC 6265 section 5.3.
An attacker who controls any server that the victim application contacts can inject a cookie scoped to an arbitrary third-party domain; because the session store performs no cross-domain ownership check, it stores and later transmits that cookie to the targeted domain.




When the victim application subsequently sends a request to the targeted domain using the same WebClientSession, it presents the attacker-injected cookie, causing the receiving service to process the request under the attacker's account. Sensitive data included in the victim application's requests, such as payment amounts, card details, or other API payloads, may then be accessible to the attacker through their own account on that service.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/162
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15076.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15076
- https://github.com/vert-x3/vertx-web

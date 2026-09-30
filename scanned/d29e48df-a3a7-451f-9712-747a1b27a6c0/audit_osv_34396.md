# [H] AliasVault Vulnerable to Server-Side Request Forgery via Favicon Extraction

## Summary
Severity: High
Advisory: CVE-2025-59344
Aliases: GHSA-f253-f7xc-w7pj
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-59344
Type: osv

## Details
AliasVault is a privacy-first password manager with built-in email aliasing. A server-side request forgery (SSRF) vulnerability exists in the favicon extraction feature of AliasVault API versions 0.23.0 and lower. The extractor fetches a user-supplied URL, parses the returned HTML, and follows <link rel="icon" href="…">. Although the initial URL is validated to allow only HTTP/HTTPS with default ports, the extractor automatically follows redirects and does not block requests to loopback or internal IP ranges. An authenticated, low-privileged user can exploit this behavior to coerce the backend into making HTTP(S) requests to arbitrary internal hosts and non-default ports. If the target host serves a favicon or any other valid image, the response is returned to the attacker in Base64 form. Even when no data is returned, timing and error behavior can be abused to map internal services. This vulnerability only affects self-hosted AliasVault instances that are reachable from the public internet with public user registration enabled. Private/internal deployments without public sign-ups are not directly exploitable. This issue has been fixed in AliasVault release 0.23.1.

## References
- https://github.com/aliasvault/aliasvault/releases/tag/0.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59344.json
- https://github.com/aliasvault/aliasvault/security/advisories/GHSA-f253-f7xc-w7pj
- https://nvd.nist.gov/vuln/detail/CVE-2025-59344
- https://github.com/aliasvault/aliasvault/commit/58c39815e4c8bb27a311c3b592d54e157b4e6968
- https://github.com/aliasvault/aliasvault/pull/1226

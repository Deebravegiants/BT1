# [C] cors-anywhere vulnerable to server-side request forgery

## Summary
Severity: Critical
Advisory: GHSA-r3jv-xfgx-gj24
CVE: CVE-2020-36851
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-r3jv-xfgx-gj24
Type: github-advisory

## Affected
- npm: `cors-anywhere` — affected >=0

## Details
Rob -- W / cors-anywhere instances configured as an open proxy allow unauthenticated external users to induce the server to make HTTP requests to arbitrary targets (SSRF). Because the proxy forwards requests and headers, an attacker can reach internal-only endpoints and link-local metadata services, retrieve instance role credentials or other sensitive metadata, and interact with internal APIs and services that are not intended to be internet-facing. The vulnerability is exploitable by sending crafted requests to the proxy with the target resource encoded in the URL; many cors-anywhere deployments forward arbitrary methods and headers (including PUT), which can permit exploitation of IMDSv2 workflows as well as access to internal management APIs. Successful exploitation can result in theft of cloud credentials, unauthorized access to internal services, remote code execution or privilege escalation (depending on reachable backends), data exfiltration, and full compromise of cloud resources. Mitigation includes: restricting the proxy to trusted origins or authentication, whitelisting allowed target hosts, preventing access to link-local and internal IP ranges, removing support for unsafe HTTP methods/headers, enabling cloud provider mitigations, and deploying network-level protections.

## References
- https://github.com/SocketDev/security-research/security/advisories/GHSA-9wmg-93pw-fc3g
- https://nvd.nist.gov/vuln/detail/CVE-2020-36851
- https://github.com/Rob--W/cors-anywhere/issues/152
- https://github.com/Rob--W/cors-anywhere/issues/521
- https://github.com/Rob--W/cors-anywhere/issues/78
- https://github.com/Rob--W/cors-anywhere
- https://www.certik.com/resources/blog/cors-anywhere-dangers-of-misconfigured-third-party-software
- https://www.vulncheck.com/advisories/rob-w-cors-anywhere-misconfigured-cors-proxy-allows-ssrf

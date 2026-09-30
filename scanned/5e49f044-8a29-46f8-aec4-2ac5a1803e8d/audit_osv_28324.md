# [C] Plane Server-Side Request Forgery (SSRF) Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-31461
Aliases: GHSA-j77v-w36v-63v6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-31461
Type: osv

## Details
Plane, an open-source project management tool, has a Server-Side Request Forgery (SSRF) vulnerability in versions prior to 0.17-dev. This issue may allow an attacker to send arbitrary requests from the server hosting the application, potentially leading to unauthorized access to internal systems. The impact of this vulnerability includes, but is not limited to, unauthorized access to internal services accessible from the server, potential leakage of sensitive information from internal services, manipulation of internal systems by interacting with internal APIs. Version 0.17-dev contains a patch for this issue. Those who are unable to update immediately may mitigate the issue by restricting outgoing network connections from servers hosting the application to essential services only and/or implementing strict input validation on URLs or parameters that are used to generate server-side requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31461.json
- https://github.com/makeplane/plane/security/advisories/GHSA-j77v-w36v-63v6
- https://nvd.nist.gov/vuln/detail/CVE-2024-31461
- https://securitylab.github.com/advisories/GHSL-2023-257_makeplane_plane
- https://github.com/makeplane/plane/commit/4b0ccea1461b7ca38761dfe0d0f07c2f94425005
- https://github.com/makeplane/plane/commit/d887b780aea5efba3f3d28c47d7d83f8b3e1e21c
- https://github.com/makeplane/plane/pull/3323
- https://github.com/makeplane/plane/pull/3333

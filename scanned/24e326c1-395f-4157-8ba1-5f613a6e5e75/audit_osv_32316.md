# [H] Server Side Request Forgery in Ziti Console

## Summary
Severity: High
Advisory: CVE-2025-27501
Aliases: GHSA-fqxh-vfv5-8qjp
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-27501
Type: osv

## Details
OpenZiti is a free and open source project focused on bringing zero trust to any application. An endpoint on the admin panel can be accessed without any form of authentication. This endpoint accepts a user-supplied URL parameter to connect to an OpenZiti Controller and performs a server-side request, resulting in a potential Server-Side Request Forgery (SSRF) vulnerability. The fixed version has moved the request to the external controller from the server side to the client side, thereby eliminating the identity of the node from being used to gain any additional permissions. This vulnerability is fixed in 3.7.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27501.json
- https://github.com/openziti/ziti-console/security/advisories/GHSA-fqxh-vfv5-8qjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-27501

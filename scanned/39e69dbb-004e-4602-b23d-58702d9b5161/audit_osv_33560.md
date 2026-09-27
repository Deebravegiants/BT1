# [H] Privilege escalation via SSRF when using HTTP auth

## Summary
Severity: High
Advisory: CVE-2025-46341
Aliases: GHSA-w3m8-wcf4-h8vm
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2025-06-04
Source: https://osv.dev/vulnerability/CVE-2025-46341
Type: osv

## Details
FreshRSS is a self-hosted RSS feed aggregator. Prior to version 1.26.2, when the server is using HTTP auth via reverse proxy, it's possible to impersonate any user either via the `Remote-User` header or the `X-WebAuth-User` header by making specially crafted requests via the add feed functionality and obtaining the CSRF token via XPath scraping. The attacker has to know the IP address of the proxied FreshRSS instance and the admin's username, while also having an account on the instance. An attacker can send specially crafted requests in order to gain unauthorized access to internal services. This can also lead to privilege escalation like in the demonstrated scenario, although users that have setup OIDC are not affected by privilege escalation. Version 1.26.2 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46341.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-w3m8-wcf4-h8vm
- https://nvd.nist.gov/vuln/detail/CVE-2025-46341
- https://github.com/FreshRSS/FreshRSS/commit/6bb8680ae0051b9a2ff344f17814f4fa5d844628

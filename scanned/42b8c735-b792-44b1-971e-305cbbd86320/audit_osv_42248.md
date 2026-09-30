# [C] KubePi: Unauthenticated SSO/OIDC configuration allows admin account takeover and SSRF

## Summary
Severity: Critical
Advisory: CVE-2026-65956
Aliases: GHSA-wjrh-4j52-c664
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-65956
Type: osv

## Details
KubePi is a Kubernetes multi-cluster management panel. In versions up to and including 1.6.15, the SSO configuration API endpoints are exposed on the same public routing boundary as the SSO login and callback endpoints, so SSO, OIDC, and SAML management operations can be reached without administrator authorization. Because reading, creating, and updating the global SSO configuration is not restricted to administrators, an unauthorized or low-privileged user can inspect or alter the authentication configuration, which under certain conditions can lead to account takeover or privilege escalation. The SSO connectivity-test function can additionally be abused as a server-side request forgery primitive, and the user list API returns user objects without consistently clearing authentication-related fields. This issue is fixed in version 2.0.0.

## References
- https://github.com/1Panel-dev/KubePi/releases/tag/v2.0.0
- https://github.com/1Panel-dev/KubePi/security/advisories/GHSA-wjrh-4j52-c664
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65956.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65956
- https://github.com/1Panel-dev/KubePi/commit/b62b41f82659e36102fccd215b13264b2035f1ea

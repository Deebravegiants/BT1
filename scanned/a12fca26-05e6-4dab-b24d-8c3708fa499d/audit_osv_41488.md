# [C] Apache CXF: OAuth2 Dynamic Client Registration Scope Self-Escalation

## Summary
Severity: Critical
Advisory: CVE-2026-61466
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-61466
Type: osv

## Details
In Apache CXF's OAuth2 Dynamic Client Registration endpoint, the authorization server accepts and stores the `scope` value supplied in the client registration request verbatim, without validating it against an AS-defined allowlist. This could lead to a client self-assigning privileged scopes at registration time. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/21
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61466.json
- https://lists.apache.org/thread/2l1r16g79tpxd7fzrzr2q9oscwrjgljs
- https://nvd.nist.gov/vuln/detail/CVE-2026-61466

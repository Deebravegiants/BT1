# [M] Improper Access Control in infinispan-server-runtime

## Summary
Severity: Medium
Advisory: GHSA-8674-26jc-wh98
CVE: CVE-2020-25711
CWE: CWE-269, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-8674-26jc-wh98
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-core` — affected >=0 <11.0.6.Final

## Details
A flaw was found in infinispan 10 REST API, where authorization permissions are not checked while performing some server management operations. When authz is enabled, any user with authentication can perform operations like shutting down the server without the ADMIN role.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25711
- https://bugzilla.redhat.com/show_bug.cgi?id=1897618
- https://security.netapp.com/advisory/ntap-20220210-0023

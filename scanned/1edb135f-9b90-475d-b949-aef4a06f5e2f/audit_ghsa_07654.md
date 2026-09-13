# [H] Wildfly Elytron integration susceptible to brute force attacks via CLI

## Summary
Severity: High
Advisory: GHSA-qhp6-6p8p-2rqh
CVE: CVE-2025-23368
CWE: CWE-307
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-qhp6-6p8p-2rqh
Type: github-advisory

## Affected
- Maven: `org.wildfly.core:wildfly-elytron-integration` — affected >=32.0.0.Beta1 <32.0.0.Beta3
- Maven: `org.wildfly.core:wildfly-elytron-integration` — affected >=0 <31.0.3.Final

## Details
### Impact

A flaw was found in Wildfly Elytron integration. The component does not implement sufficient measures to prevent multiple failed authentication attempts within a short time frame, making it more susceptible to brute force attacks via CLI.

### Patches

The default behaviour has been changed in WildFly Core 31.0.3.Final, and 32.0.0.Beta3 - the first version is used by WildFly 39.0.1.Final and the second will be included in WildFly 40.

### Workarounds

No direct workaround.
Monitoring network traffic / blocking suspicious traffic may help.

### References

https://www.cve.org/CVERecord?id=CVE-2025-23368
https://issues.redhat.com/browse/WFCORE-7192

### Acknowledgements

We would like to thank Claudia Bartolini (TIM S.p.A), Marco Ventura (TIM S.p.A), and Massimiliano Brolli (TIM S.p.A) for reporting this issue.

## References
- https://github.com/wildfly/wildfly-core/security/advisories/GHSA-qhp6-6p8p-2rqh
- https://nvd.nist.gov/vuln/detail/CVE-2025-23368
- https://github.com/wildfly/wildfly-core/pull/6634
- https://github.com/wildfly/wildfly-core/pull/6635
- https://github.com/wildfly/wildfly-core/commit/11e873031c522a0b36afb59880ce4dd59efd0bc0
- https://github.com/wildfly/wildfly-core/commit/a6f9d7534aa44de741337756f8377ad3a81f7695
- https://access.redhat.com/security/cve/CVE-2025-23368
- https://bugzilla.redhat.com/show_bug.cgi?id=2337621
- https://github.com/wildfly/wildfly-core
- https://www.gruppotim.it/it/footer/red-team.html

# [H] WildFly vulnerable to Insecure Default Initialization of Resource

## Summary
Severity: High
Advisory: GHSA-fmq7-gh8v-mjvc
CVE: CVE-2022-1278
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-fmq7-gh8v-mjvc
Type: github-advisory

## Affected
- Maven: `org.wildfly.bom:wildfly` — affected >=0 <27.0.0.Beta1

## Details
A flaw was found in WildFly, where an attacker can see deployment names, endpoints, and any other data the trace payload may contain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1278
- https://bugzilla.redhat.com/show_bug.cgi?id=2073401
- https://github.com/wildfly/boms
- https://issues.redhat.com/browse/WFLY-16238

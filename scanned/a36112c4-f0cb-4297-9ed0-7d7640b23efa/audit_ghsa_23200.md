# [H] Wildfly Unsafe Deserialization Vulnerability

## Summary
Severity: High
Advisory: GHSA-vrmw-2xhq-hrmp
CVE: CVE-2020-10740
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vrmw-2xhq-hrmp
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-parent` — affected >=0 <20.0.0.Final

## Details
A vulnerability was found in Wildfly in versions before 20.0.0.Final, where a remote deserialization attack is possible in the Enterprise Application Beans(EJB) due to lack of validation/filtering capabilities in wildfly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10740
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10740
- https://github.com/wildfly/wildfly

# [H] Improper Limitation of a Pathname to a Restricted Directory in Jboss EAP Undertow

## Summary
Severity: High
Advisory: GHSA-prfw-3qx6-g9xr
CVE: CVE-2018-1048
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-prfw-3qx6-g9xr
Type: github-advisory

## Affected
- Maven: `org.jboss.eap:wildfly-undertow` — affected >=7.1.0.GA <7.1.1.GA

## Details
It was found that the AJP connector in undertow, as shipped in Jboss EAP 7.1.0.GA, does not use the ALLOW_ENCODED_SLASH option and thus allow the the slash / anti-slash characters encoded in the url which may lead to path traversal and result in the information disclosure of arbitrary local files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1048
- https://access.redhat.com/errata/RHSA-2018:0478
- https://access.redhat.com/errata/RHSA-2018:0479
- https://access.redhat.com/errata/RHSA-2018:0480
- https://access.redhat.com/errata/RHSA-2018:0481
- https://bugzilla.redhat.com/show_bug.cgi?id=1534343

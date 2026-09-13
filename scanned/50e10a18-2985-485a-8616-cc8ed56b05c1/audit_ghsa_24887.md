# [C] Password in config file in KIE server

## Summary
Severity: Critical
Advisory: GHSA-pjw3-c74j-m9fj
CVE: CVE-2016-7043
CWE: CWE-260
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pjw3-c74j-m9fj
Type: github-advisory

## Affected
- Maven: `org.kie.server:kie-server-common` — affected >=0 <7.21.0.Final

## Details
It has been reported that KIE server and Busitess Central before version 7.21.0.Final contain username and password as plaintext Java properties. Any app deployed on the same server would have access to these properties, thus granting access to ther services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7043
- https://github.com/kiegroup/droolsjbpm-integration/pull/1273
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7043

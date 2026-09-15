# [H] Deserialization of Untrusted Data in org.jboss.resteasy:resteasy-yaml-provider

## Summary
Severity: High
Advisory: GHSA-m2fv-3rqm-g7p5
CVE: CVE-2018-1051
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m2fv-3rqm-g7p5
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-yaml-provider` — affected >=0 <3.0.26.Final
- Maven: `org.jboss.resteasy:resteasy-yaml-provider` — affected >=3.1.0 <3.6.0.Final

## Details
It was found that the fix for CVE-2016-9606 in versions 3.0.22 and 3.1.2 was incomplete and Yaml unmarshalling in Resteasy is still possible via `Yaml.load()` in YamlProvider.

#### Mitigation:   
If the YamlProvider is enabled it's recommended to add authentication, and authorization to the endpoint expecting Yaml content to prevent exploitation of this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1051
- https://github.com/resteasy/resteasy/pull/1555
- https://bugzilla.redhat.com/show_bug.cgi?id=1535411
- https://bugzilla.redhat.com/show_bug.cgi?id=1539175#c3

# [M] Unsafe methods in the default list of approved signatures in Jenkins Script Security Plugin

## Summary
Severity: Medium
Advisory: GHSA-m68x-cc2f-gr5h
CVE: CVE-2017-1000095
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m68x-cc2f-gr5h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.29.1

## Details
The default whitelist included the following unsafe entries: DefaultGroovyMethods.putAt(Object, String, Object); DefaultGroovyMethods.getAt(Object, String). These allowed circumventing many of the access restrictions implemented in the script sandbox by using e.g. currentBuild['rawBuild'] rather than currentBuild.rawBuild. Additionally, the following entries allowed accessing private data that would not be accessible otherwise due to script security: groovy.json.JsonOutput.toJson(Closure); groovy.json.JsonOutput.toJson(Object).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000095
- https://jenkins.io/security/advisory/2017-07-10

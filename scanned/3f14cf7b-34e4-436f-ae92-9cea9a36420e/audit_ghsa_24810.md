# [H] Jenkins Cadence vManager Plugin disables SSL/TLS and hostname verification 

## Summary
Severity: High
Advisory: GHSA-5j9f-5wmp-7f8h
CVE: CVE-2019-10446
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5j9f-5wmp-7f8h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vmanager-plugin` — affected >=0 <2.7.1

## Details
Jenkins Cadence vManager Plugin prior to version 2.7.1 disables SSL/TLS and hostname verification globally for the Jenkins master JVM. This issue is patched in 2.7.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10446
- https://github.com/jenkinsci/vmanager-plugin/commit/639aa135ab57d9e23c5bedeb0a5e9518eb0f486e
- https://github.com/jenkinsci/vmanager-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1615

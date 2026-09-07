# [M] Jenkins Google Compute Engine Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x24m-wr2f-p3vc
CVE: CVE-2019-16548
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x24m-wr2f-p3vc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-compute-engine` — affected >=0 <4.2.0

## Details
A cross-site request forgery vulnerability in Jenkins Google Compute Engine Plugin 4.1.1 and earlier in ComputeEngineCloud#doProvision could be used to provision new agents. Google Compute Engine Plugin 4.2.0 requires POST requests for this API endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16548
- https://github.com/jenkinsci/google-compute-engine-plugin/commit/aaf81996741c67229982f70b3eaa83894e035025
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1586
- http://www.openwall.com/lists/oss-security/2019/11/21/1

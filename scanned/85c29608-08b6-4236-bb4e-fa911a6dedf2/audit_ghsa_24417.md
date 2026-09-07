# [M] Jenkins Fortify on Demand Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-hhhh-69qp-5p2v
CVE: CVE-2019-10449
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hhhh-69qp-5p2v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify-on-demand-uploader` — affected >=0 <5.0.0

## Details
Jenkins Fortify on Demand Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10449
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/277642040362bcc64df163bfc1ab48f7763c2853
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin/commit/83b23662dc0ce9486b904e282bd8047496730819
- https://github.com/jenkinsci/fortify-on-demand-uploader-plugin
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1433

# [H] XXE vulnerability in Jenkins Compuware Topaz for Total Test Plugin

## Summary
Severity: High
Advisory: GHSA-vhwv-8897-jm7q
CVE: CVE-2022-43430
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-vhwv-8897-jm7q
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-topaz-for-total-test` — affected >=0 <2.4.9

## Details
Compuware Topaz for Total Test Plugin 2.4.8 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control the input files for the 'Topaz for Total Test - Execute Total Test scenarios' build step to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43430
- https://github.com/jenkinsci/compuware-topaz-for-total-test-plugin/commit/9ce24fb63fcdb94290340d2ec53f478635c416ab
- https://github.com/jenkinsci/compuware-topaz-for-total-test-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2625
- http://www.openwall.com/lists/oss-security/2022/10/19/3

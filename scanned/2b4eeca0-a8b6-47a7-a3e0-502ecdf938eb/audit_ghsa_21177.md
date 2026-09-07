# [M] Jenkins Compuware zAdviser API Plugin vulnerable to protection mechanism failure

## Summary
Severity: Medium
Advisory: GHSA-5xp2-7qfc-fwgc
CVE: CVE-2022-36900
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-5xp2-7qfc-fwgc
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-zadviser-api` — affected >=0 <1.0.4

## Details
Jenkins Compuware zAdviser API Plugin defines a controller/agent message that retrieves Java system properties.

Compuware zAdviser API Plugin 1.0.3 and earlier does not restrict execution of the controller/agent message to agents. This allows attackers able to control agent processes to retrieve Java system properties.

Compuware zAdviser API Plugin 1.0.4 does not allow the affected controller/agent message to be submitted by agents for execution on the controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36900
- https://github.com/jenkinsci/compuware-zadviser-api-plugin/commit/0aff2c33476b55b30e1fa9bb0eacf2f9f70ed0a8
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2630
- http://www.openwall.com/lists/oss-security/2022/07/27/1

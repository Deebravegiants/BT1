# [M] Agent-to-controller security bypass vulnerability in Jenkins Compuware Topaz Utilities Plugin

## Summary
Severity: Medium
Advisory: GHSA-2x49-wj38-78q9
CVE: CVE-2022-43422
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-2x49-wj38-78q9
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-topaz-utilities` — affected >=0 <1.0.9

## Details
Compuware Topaz Utilities Plugin 1.0.8 and earlier implements an agent/controller message that does not limit where it can be executed.

It allows attackers able to control agent processes to obtain the values of Java system properties from the Jenkins controller process.

This vulnerability is only exploitable in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#upgrading-to-jenkins-lts-2-303-3).

Compuware Topaz Utilities Plugin 1.0.9 restricts execution of the agent/controller message to agents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43422
- https://github.com/jenkinsci/compuware-topaz-utilities-plugin/commit/a91bae5fcfb17d2d0af0c86c2870f10b2bb9c20a
- https://github.com/jenkinsci/compuware-topaz-utilities-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2620
- http://www.openwall.com/lists/oss-security/2022/10/19/3

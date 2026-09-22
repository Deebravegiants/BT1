# [M] Agent-to-controller security bypass in Jenkins BMC Compuware ISPW Operations plugin

## Summary
Severity: Medium
Advisory: GHSA-57f2-52wj-7vj6
CVE: CVE-2022-36899
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-57f2-52wj-7vj6
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-ispw-operations` — affected >=0 <1.0.9

## Details
BMC Compuware ISPW Operations Plugin defines a controller/agent message that retrieves Java system properties. BMC Compuware ISPW Operations Plugin 1.0.8 and earlier does not restrict execution of the controller/agent message to agents. This allows attackers able to control agent processes to retrieve Java system properties. This vulnerability is only exploitable in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#upgrading-to-jenkins-lts-2-303-3). BMC Compuware ISPW Operations plugin 1.0.9 does not allow the affected controller/agent message to be submitted by agents for execution on the controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36899
- https://github.com/jenkinsci/compuware-ispw-operations-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2629
- http://www.openwall.com/lists/oss-security/2022/07/27/1

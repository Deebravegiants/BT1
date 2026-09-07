# [C] Unsafe entry in Script Security list of approved signatures in Pipeline Remote Loader Plugin

## Summary
Severity: Critical
Advisory: GHSA-v558-fhw2-v46w
CVE: CVE-2019-10328
CWE: CWE-183, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v558-fhw2-v46w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:workflow-remote-loader` — affected >=0 <1.5

## Details
Jenkins Pipeline Remote Loader Plugin before 1.5 provided a custom whitelist for script security that allowed attackers to invoke arbitrary methods, bypassing typical sandbox protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10328
- https://github.com/jenkinsci/workflow-remote-loader-plugin/commit/6f9d60f614359720ec98e22b80ba15e8bf88e712
- https://access.redhat.com/errata/RHBA-2019:1605
- https://access.redhat.com/errata/RHSA-2019:1636
- https://github.com/jenkinsci/workflow-remote-loader-plugin
- https://jenkins.io/security/advisory/2019-05-31/#SECURITY-921
- http://www.openwall.com/lists/oss-security/2019/05/31/2
- http://www.securityfocus.com/bid/108540

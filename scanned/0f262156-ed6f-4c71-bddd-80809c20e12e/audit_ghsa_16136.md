# [H] Rebuilding a run with revoked script approval allowed by Jenkins Pipeline: Groovy Plugin 

## Summary
Severity: High
Advisory: GHSA-mrpr-vr82-x88r
CVE: CVE-2024-52550
CWE: CWE-285, CWE-354
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-mrpr-vr82-x88r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps` — affected >=0 <3993.v3e20a

## Details
Jenkins Pipeline: Groovy Plugin 3990.vd281dd77a_388 and earlier, except 3975.3977.v478dd9e956c3 does not check whether the main (Jenkinsfile) script for a rebuilt build is approved, allowing attackers with Item/Build permission to rebuild a previous build whose (Jenkinsfile) script is no longer approved. This allows attackers with Item/Build permission to rebuild a previous build whose (Jenkinsfile) script is no longer approved. Pipeline: Groovy Plugin 3993.v3e20a_37282f8 refuses to rebuild a build whose main (Jenkinsfile) script is unapproved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52550
- https://github.com/jenkinsci/workflow-cps-plugin
- https://www.jenkins.io/security/advisory/2024-11-13/#SECURITY-3362

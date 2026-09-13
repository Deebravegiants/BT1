# [H] Restarting a run with revoked script approval allowed by Jenkins Pipeline: Declarative Plugin 

## Summary
Severity: High
Advisory: GHSA-p2qq-c693-q53w
CVE: CVE-2024-52551
CWE: CWE-276, CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-p2qq-c693-q53w
Type: github-advisory

## Affected
- Maven: `org.jenkinsci.plugins:pipeline-model-parent` — affected >=0 <2.2218.v56d0cda

## Details
Jenkins Pipeline: Declarative Plugin 2.2214.vb_b_34b_2ea_9b_83 and earlier does not check whether the main (Jenkinsfile) script used to restart a build from a specific stage is approved, allowing attackers with Item/Build permission to restart a previous build whose (Jenkinsfile) script is no longer approved. This allows attackers with Item/Build permission to restart a previous build whose (Jenkinsfile) script is no longer approved. Pipeline: Declarative Plugin 2.2218.v56d0cda_37c72 refuses to restart a build whose main (Jenkinsfile) script is unapproved.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52551
- https://github.com/jenkinsci/pipeline-model-definition-plugin
- https://www.jenkins.io/security/advisory/2024-11-13/#SECURITY-3361

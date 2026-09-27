# [M] Jenkins Pipeline: Groovy Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-qv6q-x9vr-w7j3
CVE: CVE-2022-25180
CWE: CWE-319, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-qv6q-x9vr-w7j3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps` — affected >=0 <2656.vf7a_e7b_75a_457

## Details
Jenkins Pipeline: Groovy Plugin 2648.va9433432b33c and earlier includes password parameters from the original build in replayed builds.

This allows attackers with Run/Replay permission to obtain the values of password parameters passed to previous builds of a Pipeline.

Pipeline: Groovy Plugin 2656.vf7a_e7b_75a_457 does not allow builds containing password parameters to be replayed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25180
- https://github.com/jenkinsci/workflow-cps-plugin/commit/886676efdd711e126307ec70a539f2fe613151f9
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2443

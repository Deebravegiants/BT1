# [M] BIT-jenkins-2026-84651

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-84651
Aliases: CVE-2026-84651
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84651
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, the REST API and CLI endpoints for updating agent configuration do not prevent a submitted configuration from overwriting a different agent by specifying that agent's name in the submitted XML document, allowing attackers with Agent/Configure permission on one agent to take over a different agent, gaining control of its configuration and obtaining access to its inbound agent secret and environment variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84651
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-4025

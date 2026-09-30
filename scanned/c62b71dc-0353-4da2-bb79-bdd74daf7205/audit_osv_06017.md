# [H] BIT-jenkins-2026-84645

## Summary
Severity: High
Advisory: BIT-jenkins-2026-84645
Aliases: CVE-2026-84645
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84645
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, objects of types marked as storing their configuration in independent top-level configuration files in Jenkins (such as the global configuration and jobs) can appear as nested field values in user-submitted `config.xml` documents and subsequently handle HTTP requests via Stapler, resulting in remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84645
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-3972

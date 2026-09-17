# [M] BIT-jenkins-2026-84655

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-84655
Aliases: CVE-2026-84655
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84655
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
Jenkins 2.579 and earlier, LTS 2.568.2 and earlier does not escape map keys when serializing objects as JSON and Python through its REST API, allowing attackers able to control map property names to inject arbitrary fields into JSON and Python API responses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84655
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-3879

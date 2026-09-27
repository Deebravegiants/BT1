# [H] BIT-jenkins-2026-84652

## Summary
Severity: High
Advisory: BIT-jenkins-2026-84652
Aliases: CVE-2026-84652
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84652
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, Jenkins does not rotate the session when a user is authenticated via the "remember me" cookie, allowing attackers able to serve content on the same site as Jenkins to set a known session cookie in the victim's browser, which after the victim authenticates via the "remember me" cookie, grants the attacker access to Jenkins as that user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84652
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-4016

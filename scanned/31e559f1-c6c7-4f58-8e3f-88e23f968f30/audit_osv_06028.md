# [M] BIT-jenkins-2026-84657

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-84657
Aliases: CVE-2026-84657
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84657
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, the build CLI command does not check the Item/Cancel permission when using the -s flag to cancel a build triggered to wait for completion, allowing attackers with Item/Build permission to cancel builds started by other users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84657
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-4015

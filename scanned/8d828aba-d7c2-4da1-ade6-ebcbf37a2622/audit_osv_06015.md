# [M] BIT-jenkins-2026-70428

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-70428
Aliases: CVE-2026-70428
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-70428
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.576.0

## Details
Jenkins 2.575 and earlier, LTS 2.568.1 and earlier improperly identifies file paths attempting path traversal in file parameter names, allowing attackers with Item/Configure and Item/Build permission to write files to arbitrary locations on the controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-70428
- https://www.jenkins.io/security/advisory/2026-08-05/#SECURITY-3927

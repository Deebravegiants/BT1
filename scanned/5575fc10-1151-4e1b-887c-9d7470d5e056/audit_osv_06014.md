# [M] BIT-jenkins-2026-70427

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-70427
Aliases: CVE-2026-70427
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-70427
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.576.0

## Details
Jenkins 2.575 and earlier, LTS 2.568.1 and earlier does not safely handle symbolic links with effectively empty names during the extraction of `.tar` and `.tar.gz` archives, allowing attackers able to control agent processes to provide crafted archives to the controller to write files to arbitrary locations on the file system, restricted only by file system access permissions of the user running Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-70427
- https://www.jenkins.io/security/advisory/2026-08-05/#SECURITY-3930

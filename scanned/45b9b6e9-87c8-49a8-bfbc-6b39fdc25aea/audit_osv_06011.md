# [M] BIT-jenkins-2025-67637

## Summary
Severity: Medium
Advisory: BIT-jenkins-2025-67637
Aliases: CVE-2025-67637, GHSA-fxj7-6v9w-xc76
Ecosystem: Bitnami
Published: 2025-12-12
Source: https://osv.dev/vulnerability/BIT-jenkins-2025-67637
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.529.0 <2.541.0

## Details
Jenkins 2.540 and earlier, LTS 2.528.2 and earlier stores build authorization tokens unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67637
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-783

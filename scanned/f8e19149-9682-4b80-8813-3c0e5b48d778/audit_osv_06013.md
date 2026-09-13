# [C] BIT-jenkins-2026-70426

## Summary
Severity: Critical
Advisory: BIT-jenkins-2026-70426
Aliases: CVE-2026-70426
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-70426
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.576.0

## Details
In Remoting 3384.v60d89463d9e0 and earlier, except 3355.3357.v931d3c992987, included in Jenkins 2.575 and earlier, LTS 2.568.1 and earlier, the JEP-200 class filter is not applied to classes resolved via a fallback path in the Remoting deserialization implementation, allowing agent processes, code running on agents, and attackers with Agent/Connect permission to bypass the JEP-200 deserialization filter for classes on the Jenkins core classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-70426
- https://www.jenkins.io/security/advisory/2026-08-05/#SECURITY-3911

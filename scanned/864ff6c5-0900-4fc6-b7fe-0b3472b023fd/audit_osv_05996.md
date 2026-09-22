# [C] BIT-jenkins-2021-21694

## Summary
Severity: Critical
Advisory: BIT-jenkins-2021-21694
Aliases: CVE-2021-21694, GHSA-pgj6-jmj5-wqfx
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-jenkins-2021-21694
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=0 <2.319.0

## Details
FilePath#toURI, FilePath#hasSymlink, FilePath#absolutize, FilePath#isDescendant, and FilePath#get*DiskSpace do not check any permissions in Jenkins LTS 2.303.2 and earlier.

## References
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2455
- https://nvd.nist.gov/vuln/detail/CVE-2021-21694

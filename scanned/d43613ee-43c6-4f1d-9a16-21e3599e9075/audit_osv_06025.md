# [M] BIT-jenkins-2026-84654

## Summary
Severity: Medium
Advisory: BIT-jenkins-2026-84654
Aliases: CVE-2026-84654
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84654
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Stapler 2107.v8dfcb_e8ed317 and earlier, except 2088.2093.vd7c3e58008a_6, included in Jenkins 2.579 and earlier, LTS 2.568.2 and earlier, form data binding allows setting public static fields of the bound configuration object, allowing attackers who can submit configuration forms to modify public static fields of the configuration objects those forms are bound to, resulting in changes that apply globally to the Jenkins instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84654
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-3926

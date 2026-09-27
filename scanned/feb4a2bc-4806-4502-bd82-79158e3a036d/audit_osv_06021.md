# [H] BIT-jenkins-2026-84649

## Summary
Severity: High
Advisory: BIT-jenkins-2026-84649
Aliases: CVE-2026-84649
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-jenkins-2026-84649
Type: osv

## Affected
- Bitnami: `jenkins` — affected >=2.569.0 <2.580.0

## Details
In Stapler 1839.ved17667b_a_eb_5 through 2107.v8dfcb_e8ed317 (both inclusive), except 2088.2093.vd7c3e58008a_6, included in Jenkins 2.447 through 2.579 (both inclusive), LTS 2.452.1 through 2.568.2 (both inclusive), an HTTP endpoint serving dynamically generated JavaScript resources embeds the user's cross-site request forgery (CSRF) token (crumb) as a string literal, allowing attackers with control over a page hosted on the same site as Jenkins to obtain a valid crumb for the targeted user's session and perform actions on their behalf.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-84649
- https://www.jenkins.io/security/advisory/2026-09-02/#SECURITY-3878

# [M] BIT-limesurvey-2024-42903

## Summary
Severity: Medium
Advisory: BIT-limesurvey-2024-42903
Aliases: CVE-2024-42903
Ecosystem: Bitnami
Published: 2024-09-13
Source: https://osv.dev/vulnerability/BIT-limesurvey-2024-42903
Type: osv

## Affected
- Bitnami: `limesurvey` — affected >=0 <6.15.5

## Details
A Host header injection vulnerability in the password reset function of LimeSurvey v.6.6.1+240806 and before allows attackers to send users a crafted password reset link that will direct victims to a malicious domain.

## References
- https://github.com/LimeSurvey/LimeSurvey/compare/6.6.0+240729...6.6.1+240806
- https://github.com/LimeSurvey/LimeSurvey/pull/3920
- https://github.com/sysentr0py/CVEs/tree/main/CVE-2024-42903
- https://nvd.nist.gov/vuln/detail/CVE-2024-42903

# [H] BIT-limesurvey-2024-42902

## Summary
Severity: High
Advisory: BIT-limesurvey-2024-42902
Aliases: CVE-2024-42902
Ecosystem: Bitnami
Published: 2025-07-04
Source: https://osv.dev/vulnerability/BIT-limesurvey-2024-42902
Type: osv

## Affected
- Bitnami: `limesurvey` — affected >=0 <6.15.5

## Details
An issue in the js_localize.php function of LimeSurvey v6.6.2 and before allows attackers to execute arbitrary code via injecting a crafted payload into the lng parameter of the js_localize.php function

## References
- https://bugs.limesurvey.org/view.php?id=19639
- https://github.com/LimeSurvey/LimeSurvey/blob/6434b12ded1c4b6516200c453441d0896e11eee0/vendor/kcfinder/js_localize.php#L19
- https://github.com/sysentr0py/CVEs/tree/main/CVE-2024-42902
- https://nvd.nist.gov/vuln/detail/CVE-2024-42902

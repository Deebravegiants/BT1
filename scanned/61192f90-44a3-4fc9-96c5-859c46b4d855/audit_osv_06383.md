# [H] BIT-limesurvey-2021-44967

## Summary
Severity: High
Advisory: BIT-limesurvey-2021-44967
Aliases: CVE-2021-44967
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-limesurvey-2021-44967
Type: osv

## Affected
- Bitnami: `limesurvey` — affected >=5.2.4 <5.2.5

## Details
A Remote Code Execution (RCE) vulnerabilty exists in LimeSurvey 5.2.4 via the upload and install plugins function, which could let a remote malicious user upload an arbitrary PHP code file. NOTE: the Supplier's position is that plugins intentionally can contain arbitrary PHP code, and can only be installed by a superadmin, and therefore the security model is not violated by this finding.

## References
- https://github.com/Y1LD1R1M-1337/Limesurvey-RCE
- https://www.exploit-db.com/exploits/50573
- https://www.limesurvey.org/manual/Plugins_-_advanced
- https://nvd.nist.gov/vuln/detail/CVE-2021-44967

# [M] Multiple vulnerabilities in Limesurvey

## Summary
Severity: Medium
Advisory: BIT-limesurvey-2025-41075
Aliases: CVE-2025-41075
Ecosystem: Bitnami
Published: 2025-11-22
Source: https://osv.dev/vulnerability/BIT-limesurvey-2025-41075
Type: osv

## Affected
- Bitnami: `limesurvey` — affected >=6.13.0 <6.15.5

## Details
Vulnerability in LimeSurvey 6.13.0 in the endpoint /optin that causes infinite HTTP redirects when accessed directly. This behavior can be exploited to generate a Denegation of Service (DoS  attack), by exhausting server or client resources. The system is unable to break the redirect loop, which can cause service degradation or browser instability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41075
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-limesurvey-0

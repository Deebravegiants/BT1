# [M] CVE-2026-82955

## Summary
Severity: Medium
Advisory: CVE-2026-82955
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-82955
Type: osv

## Details
In the current development version of Eclipse aeriOS, which has not yet had an official release, the KrakenD instance included in the API Gateway component had the disable_jwk_security parameter hard-coded to true, with no option to override it through the Helm chart configuration. This setting disables TLS certificate verification when KrakenD retrieves the JSON Web Key Set (JWKS) used to validate bearer tokens, potentially allowing an attacker with the ability to intercept this communication to provide a malicious JWKS and compromise token validation.




The issue has been addressed by making the parameter configurable through the boolean Helm value krakend.config.disableJwkSecurity and setting its default value to false, ensuring that TLS certificate verification is enabled by default.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/818
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82955.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82955
- https://github.com/eclipse-aerios/api-gateway/commit/e680c69c34b82db4944517198330cc447a1e8f98

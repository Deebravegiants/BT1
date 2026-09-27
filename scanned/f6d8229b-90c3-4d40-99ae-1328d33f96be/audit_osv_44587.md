# [M] CVE-2026-84736

## Summary
Severity: Medium
Advisory: CVE-2026-84736
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-84736
Type: osv

## Details
In the current development version of Eclipse aeriOS, for which no official release has yet been published, the Federator component disables TLS certificate validation for outbound HTTPS connections by default. When the TLS_CERTIFICATE_VALIDATION environment variable is unset or set to false, the component configures its HTTP transport to skip TLS certificate verification.




As a result, an attacker able to intercept network communications between the Federator and external services could impersonate those services and intercept sensitive information transmitted over HTTPS, including OAuth client credentials and bearer tokens.




The issue has been addressed by enabling TLS certificate validation by default. The TLS_CERTIFICATE_VALIDATION environment variable is now set to true in the default configuration provided by the Helm chart and Docker Compose deployment.

## References
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/755
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84736.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84736
- https://github.com/eclipse-aerios/federator/commit/9c63b60becc9873b0195ff9cd6582b69cb12d4f2

# [H] Improper Validation of Certificate in CAS Client

## Summary
Severity: High
Advisory: CVE-2026-15243
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-15243
Type: osv

## Details
Apereo CAS Client accepts any CA-trusted certificate for any hostname, provided the URL the client is calling matches the configured allowlist or regex. An attacker with a MITM position (DNS poisoning, rogue Wi-Fi, malicious proxy, etc.) can provide any CA-signed certificate for a hostname that matches the configured allowlist or regex. This can lead to intercepting the CAS exchange, capturing the Ticket-Granting Ticket (TGT), and subsequently obtaining Service Tickets on behalf of the victim. 


Because maintainers contact attempts were unsuccessful, vulnerabilities have only been confirmed in version 4.1.0 (Java Apereo CAS Client) and 3.6.4 (Jasig CAS Client) but may also affect other versions.

## References
- https://mvnrepository.com/
- https://www.apereo.org/programs/software/cas
- https://cert.pl/en/posts/2026/07/CVE-2026-15243
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15243
- https://github.com/apereo/java-cas-client

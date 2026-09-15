# [M] iPAddress name constraints bypass when `WOLFSSL_IP_ALT_NAME` is not defined

## Summary
Severity: Medium
Advisory: JLSEC-2026-758
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-758
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
iPAddress name constraints bypass when `WOLFSSL_IP_ALT_NAME` is not defined. IP address name constraints are not enforced in that configuration, allowing a certificate to bypass an issuing CA's IP address constraints.

## References
- https://github.com/advisories/GHSA-h4jr-6mf9-63fq
- https://github.com/wolfSSL/wolfssl/pull/10354
- https://nvd.nist.gov/vuln/detail/CVE-2026-7532
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2409
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/

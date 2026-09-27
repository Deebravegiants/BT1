# [C] Ghidra < 12.1 - Authentication Bypass via Null Signature in PKIAuthenticationModule

## Summary
Severity: Critical
Advisory: CVE-2026-52754
Aliases: GHSA-5wxq-7qpv-65p2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52754
Type: osv

## Details
Ghidra before 12.1 contains an authentication bypass vulnerability in PKIAuthenticationModule.authenticate() that allows any user with a valid CA-signed certificate to impersonate other users by presenting their public certificate with a null signature. Attackers can escalate privileges, modify repository access controls, exfiltrate shared reverse engineering databases, and permanently compromise server integrity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52754.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-5wxq-7qpv-65p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-52754
- https://www.vulncheck.com/advisories/ghidra-authentication-bypass-via-null-signature-in-pkiauthenticationmodule
- https://github.com/NationalSecurityAgency/ghidra/commit/78729379e471bbb3d969409be6a8c3d24af84220
- https://github.com/NationalSecurityAgency/ghidra/commit/79d8f164f8bb8b15cfb60c5d4faeb8e1c25d15ca
- https://github.com/nationalsecurityagency/ghidra

# [H] PowerDocu Affected by Remote Code Execution via Insecure Deserialization

## Summary
Severity: High
Advisory: CVE-2026-25925
Aliases: GHSA-m8j2-5jr7-2jpw
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25925
Type: osv

## Details
PowerDocu contains a Windows GUI executable to perform technical documentations. Prior to 2.4.0, PowerDocu contains a critical security vulnerability in how it parses JSON files within Flow or App packages. The application blindly trusts the $type property in JSON files, allowing an attacker to instantiate arbitrary .NET objects and execute code. This vulnerability is fixed in 2.4.0.

## References
- https://github.com/modery/PowerDocu/releases/tag/v-2.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25925.json
- https://github.com/modery/PowerDocu/security/advisories/GHSA-m8j2-5jr7-2jpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-25925

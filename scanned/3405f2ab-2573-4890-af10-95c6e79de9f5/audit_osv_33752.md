# [M] Asterisk is Vulnerable to Remote DoS and possible RCE Attacks During Memory Allocation

## Summary
Severity: Medium
Advisory: CVE-2025-49832
Aliases: GHSA-mrq5-74j5-f5cr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-49832
Type: osv

## Details
Asterisk is an open source private branch exchange and telephony toolkit. In versions up to and including 18.26.2, between 20.00.0 and 20.15.0, 20.7-cert6, 21.00.0, 22.00.0 through 22.5.0, there is a remote DoS and possible RCE condition in `asterisk/res/res_stir_shaken /verification.c` that can be exploited when an attacker can set an arbitrary Identity header, or STIR/SHAKEN is enabled, with verification set in the SIP profile associated with the endpoint to be attacked. This is fixed in versions 18.26.3, 20.7-cert6, 20.15.1, 21.10.1 and 22.5.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49832.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-mrq5-74j5-f5cr
- https://nvd.nist.gov/vuln/detail/CVE-2025-49832

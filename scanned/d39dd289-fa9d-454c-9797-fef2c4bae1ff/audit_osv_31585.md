# [C] Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2025-14942
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/U:Red)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2025-14942
Type: osv

## Details
wolfSSH’s key exchange state machine can be manipulated to leak the client’s password in the clear, trick the client to send a bogus signature, or trick the client into skipping user authentication. This affects client applications with wolfSSH version 1.4.21 and earlier. Users of wolfSSH must update or apply the fix patch and it’s recommended to update credentials used. This fix is also recommended for wolfSSH server applications. While there aren’t any specific attacks on server applications, the same defect is present. Thanks to Aina Toky Rasoamanana of Valeo and Olivier Levillain of Telecom SudParis for the report.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14942.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14942
- https://github.com/wolfSSL/wolfssh/pull/855

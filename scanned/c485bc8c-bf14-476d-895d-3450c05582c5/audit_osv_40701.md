# [H] Leantime - Missing Authorization on TwoFA JSON-RPC Methods Allows Cross-Account 2FA Secret Disclosure and Bypass

## Summary
Severity: High
Advisory: CVE-2026-54418
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-54418
Type: osv

## Details
Leantime through 3.6.2 exposes the JSON-RPC methods leantime.rpc.TwoFA.TwoFA.getSetupData, saveSecret, verifyAndEnable, and disable2FA, which act on a caller-supplied userId parameter with no ownership check, session pinning, or permission-attribute gate (unlike other RPC-exposed methods in the same dispatcher).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54418.json
- https://github.com/Leantime/leantime
- https://nvd.nist.gov/vuln/detail/CVE-2026-54418

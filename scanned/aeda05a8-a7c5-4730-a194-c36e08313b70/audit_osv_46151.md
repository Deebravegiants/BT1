# [M] When restoring a session from cache, a pointer from the serialized session data is used in a free...

## Summary
Severity: Medium
Advisory: JLSEC-2026-733
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:H/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-733
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
When restoring a session from cache, a pointer from the serialized session data is used in a free operation without validation. An attacker who can poison the session cache could trigger an arbitrary free. Exploitation requires the ability to inject a crafted session into the cache and for the application to call specific session restore APIs.

## References
- https://github.com/advisories/GHSA-f5fh-xmxq-55p9
- https://github.com/wolfSSL/wolfssl/pull/10088
- https://nvd.nist.gov/vuln/detail/CVE-2026-5507

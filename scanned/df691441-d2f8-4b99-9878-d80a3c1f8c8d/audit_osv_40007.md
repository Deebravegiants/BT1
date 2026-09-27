# [C] Distribution-over-TLS LAN allowlist silently bypassed due to sockname/peername confusion in inet_tls_dist

## Summary
Severity: Critical
Advisory: CVE-2026-48860
Aliases: EEF-CVE-2026-48860, GHSA-gp7x-mfv6-52cv
CVSS: 9.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-48860
Type: osv

## Details
Reliance on IP Address for Authentication vulnerability in Erlang/OTP ssl (inet_tls_dist module) allows unauthenticated bypass of the distribution-over-TLS LAN allowlist.

The inet_tls_dist:check_ip/1 function, which enforces a LAN allowlist for Erlang distribution over TLS, calls inet:sockname/1 instead of inet:peername/1 to obtain the peer's IP address. Because inet:sockname/1 returns the local socket address, both the local IP and the supposed peer IP resolve to the same value, causing the subnet mask comparison to always succeed regardless of the actual remote address. Any holder of a CA-signed TLS certificate can therefore bypass the LAN restriction and gain full Erlang distribution access to the node, including rpc:call/4 and code:load_binary/3.

This vulnerability is associated with program file lib/ssl/src/inet_tls_dist.erl.

This issue affects OTP from OTP 26.0 before OTP 29.0.2, OTP 28.5.0.2 and OTP 27.3.4.13, corresponding to ssl from 11.0 before 11.7.2, 11.6.0.2 and 11.2.12.9.

## References
- https://cna.erlef.org/cves/CVE-2026-48860.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-48860
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48860.json
- https://github.com/erlang/otp/security/advisories/GHSA-gp7x-mfv6-52cv
- https://nvd.nist.gov/vuln/detail/CVE-2026-48860
- https://github.com/erlang/otp/commit/0209a6df65d605552b378273027b3968b35f26b4
- https://github.com/erlang/otp

# [M] DTLS listener crash via race condition in dtls_packet_demux causes denial of service for all sessions

## Summary
Severity: Medium
Advisory: CVE-2026-55950
Aliases: EEF-CVE-2026-55950, GHSA-hwfc-5hf4-gvr3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-55950
Type: osv

## Details
Time-of-check Time-of-use (TOCTOU) race condition vulnerability in Erlang/OTP ssl (dtls_packet_demux module) allows an unauthenticated remote attacker to crash all active DTLS sessions on a listener.

A DTLS server listener uses a single shared dtls_packet_demux gen_server process to route incoming UDP datagrams to the correct connection handler. When a DTLS client reconnects rapidly from the same source address and port (sending multiple ClientHello messages in quick succession), a race condition in the demux's internal gb_trees key-value store causes a {key_exists, {old, Client}} crash, terminating the demux process. Because the demux is shared across all DTLS associations on that listener, its crash immediately kills every active DTLS session, not just the attacker's.

The attack is pre-authentication: the attacker only needs to send UDP datagrams containing valid ClientHello messages from the same source IP and port before the intermediate DOWN monitor message is processed by the gen_server. No credentials, no completed handshake, and no special configuration are required, and the crash can be repeated indefinitely to create a persistent denial of service for all clients of that listener.

This vulnerability is associated with program file lib/ssl/src/dtls_packet_demux.erl.

This issue affects OTP from OTP 25.3 before OTP 29.0.3, OTP 28.5.0.3 and OTP 27.3.4.14, corresponding to ssl from 10.9 before 11.7.3, 11.6.0.3 and 11.2.12.10.

## References
- https://cna.erlef.org/cves/CVE-2026-55950.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55950
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55950.json
- https://github.com/erlang/otp/security/advisories/GHSA-hwfc-5hf4-gvr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-55950
- https://github.com/erlang/otp/commit/e44d2bf01c4473ef2ea7f09e3523cf96de6e4a04
- https://github.com/erlang/otp

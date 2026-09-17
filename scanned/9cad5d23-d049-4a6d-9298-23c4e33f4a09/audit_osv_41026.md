# [M] Phoenix transports do not limit channel joins per connection, enabling process-exhaustion denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-56811
Aliases: EEF-CVE-2026-56811, GHSA-6983-jfq8-485w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-56811
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in phoenixframework phoenix (Phoenix.Socket module) allows an unauthenticated attacker to cause a denial of service against any endpoint that mounts a Phoenix socket with a reachable channel transport (WebSocket or LongPoll).

This vulnerability is associated with program files lib/phoenix/socket.ex and program routine 'Elixir.Phoenix.Socket':handle_in/4.

Phoenix transports do not limit the number of channels that a single transport process may join. Every phx_join message a client sends over one connection starts a persistent channel process, and the socket process accepts an unbounded number of them. A single unauthenticated client can therefore open one WebSocket or LongPoll connection and stream a large number of phx_join messages, spawning hundreds of thousands of channel processes over that one connection and eventually reaching the BEAM maximum process limit. Once the process table is exhausted the virtual machine can no longer start new processes, denying service to legitimate traffic across the whole node. Because the amplification happens inside a single connection, network-layer connection caps and rate limiting do not mitigate it.

The fix adds a :max_channels_per_transport option (default 100) that bounds the number of channels a single transport process can join, forcing abusive clients to open many connections instead, where external load balancers and reverse proxies can throttle them.

This issue affects phoenix: from 0.11.0 before 1.5.15, from 1.6.0-rc.0 before 1.6.17, from 1.7.0-rc.0 before 1.7.24, and from 1.8.0-rc.0 before 1.8.9.

## References
- https://cna.erlef.org/cves/CVE-2026-56811.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-56811
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56811.json
- https://github.com/phoenixframework/phoenix/security/advisories/GHSA-6983-jfq8-485w
- https://nvd.nist.gov/vuln/detail/CVE-2026-56811
- https://github.com/phoenixframework/phoenix/commit/16e295d2fccab185d1292322e2bee5d46c725c8a
- https://github.com/phoenixframework/phoenix/commit/a612100cd8a4279091abc1a2ef8fb98a6d01c0a1
- https://github.com/phoenixframework/phoenix/commit/c498ba8cf49f6accbbd0c643a5340b58db891218
- https://github.com/phoenixframework/phoenix/commit/d19ca0a8d9f82c130b7ed339b9f033433e2dea5e
- https://github.com/phoenixframework/phoenix

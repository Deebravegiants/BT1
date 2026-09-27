# [H] CVE-2020-26262

## Summary
Severity: High
Advisory: CVE-2020-26262
Aliases: GHSA-6g6j-r9rf-cm7p
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2021-01-13
Source: https://osv.dev/vulnerability/CVE-2020-26262
Type: osv

## Details
Coturn is free open source implementation of TURN and STUN Server. Coturn before version 4.5.2 by default does not allow peers to connect and relay packets to loopback addresses in the range of `127.x.x.x`. However, it was observed that when sending a `CONNECT` request with the `XOR-PEER-ADDRESS` value of `0.0.0.0`, a successful response was received and subsequently, `CONNECTIONBIND` also received a successful response. Coturn then is able to relay packets to the loopback interface. Additionally, when coturn is listening on IPv6, which is default, the loopback interface can also be reached by making use of either `[::1]` or `[::]` as the peer address. By using the address `0.0.0.0` as the peer address, a malicious user will be able to relay packets to the loopback interface, unless `--denied-peer-ip=0.0.0.0` (or similar) has been specified. Since the default configuration implies that loopback peers are not allowed, coturn administrators may choose to not set the `denied-peer-ip` setting. The issue patched in version 4.5.2. As a workaround the addresses in the address block `0.0.0.0/8`, `[::1]` and `[::]` should be denied by default unless `--allow-loopback-peers` has been specified.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G54UIUFTEC6RLPOISMB6FUW7456SBZC4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M4CJOPAQT43MYAFU3UROGLEXN3Z6RS4H/
- https://github.com/coturn/coturn/blob/57180ab60afcaeb13537e69ae8cb8aefd8f3f546/ChangeLog#L48
- https://github.com/coturn/coturn/commit/abfe1fd08d78baa0947d17dac0f7411c3d948e4d
- https://github.com/coturn/coturn/security/advisories/GHSA-6g6j-r9rf-cm7p

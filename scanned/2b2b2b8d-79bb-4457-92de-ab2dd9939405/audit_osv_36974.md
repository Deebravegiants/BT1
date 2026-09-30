# [H] Coturn: IPv4-mapped IPv6 (::ffff:0:0/96) bypasses denied-peer-ip ACL

## Summary
Severity: High
Advisory: CVE-2026-27624
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27624
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Coturn is commonly configured to block loopback and internal ranges using "denied-peer-ip" and/or default loopback restrictions. CVE-2020-26262 addressed bypasses involving "0.0.0.0", "[::1]" and "[::]", but IPv4-mapped IPv6 is not covered. When sending a "CreatePermission" or "ChannelBind" request with the "XOR-PEER-ADDRESS" value of "::ffff:127.0.0.1", a successful response is received, even though "127.0.0.0/8" is blocked via "denied-peer-ip". The root cause is that, prior to the updated fix implemented in version 4.9.0, three functions in "src/client/ns_turn_ioaddr.c" do not check "IN6_IS_ADDR_V4MAPPED". "ioa_addr_is_loopback()" checks "127.x.x.x" (AF_INET) and "::1" (AF_INET6), but not "::ffff:127.0.0.1." "ioa_addr_is_zero()" checks "0.0.0.0" and "::", but not "::ffff:0.0.0.0." "addr_less_eq()" used by "ioa_addr_in_range()" for "denied-peer-ip" matching: when the range is AF_INET and the peer is AF_INET6, the comparison returns 0 without extracting the embedded IPv4. Version 4.9.0 contains an updated fix to address the bypass of the fix for CVE-2020-26262.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27624.json
- https://github.com/coturn/coturn/security/advisories/GHSA-6g6j-r9rf-cm7p
- https://github.com/coturn/coturn/security/advisories/GHSA-j8mm-mpf8-gvjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-27624
- https://github.com/coturn/coturn/commit/b80eb898ba26552600770162c26a8ae7f3661b0b

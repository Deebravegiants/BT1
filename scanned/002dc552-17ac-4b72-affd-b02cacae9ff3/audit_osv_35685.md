# [H] Out-of-bounds write in IPv6 6LoWPAN Context Option handling via unauthenticated Router Advertisement

## Summary
Severity: High
Advisory: CVE-2026-12633
Aliases: GHSA-h5m5-hm6j-cgpf
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-12633
Type: osv

## Details
The IPv6 neighbor-discovery code in subsys/net/ip/ipv6_nbr.c processes the 6LoWPAN Context Option (6CO, RFC 6775) carried inside ICMPv6 Router Advertisements. In handle_ra_6co() the 8-bit context_len field is taken directly from the packet and was never bounded to the RFC maximum of 128. The function computes context->context_len / 8 and then performs memset(context->prefix + context_len, 0, sizeof(context->prefix) - context_len), where context->prefix is a fixed 16-byte array.

With context_len between 136 and 255 (and the option length field set to 3, which the pre-fix validation accepts), context_len / 8 evaluates to 17..31, so the memset length 16 - context_len/8 underflows the unsigned size_t argument to roughly SIZE_MAX. This produces an unbounded out-of-bounds memset that zeroes kernel memory well past the 6lo context structure.

The defect is reachable from unauthenticated, link-local input: any host on the same link can send a crafted Router Advertisement with a 6CO option. The RA handler validates only the option length field before calling handle_ra_6co(), so a single packet triggers the wild write. The code is compiled when CONFIG_NET_6LO_CONTEXT is enabled.

The impact is a reliable remote (adjacent) denial of service via memory corruption, with collateral integrity loss as the memset zeroes contiguous memory before the system faults. Router Advertisements are link-scoped and not forwarded, so the attacker must be on the same link (AV:A). The fix rejects any context_len greater than 128 before the length computation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12633.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-h5m5-hm6j-cgpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-12633
- https://github.com/zephyrproject-rtos/zephyr/commit/15e838c739be637bf23fd56a5c26f2b32079551b
- https://github.com/zephyrproject-rtos/zephyr

# [H] Stack buffer overflow in `net_ipaddr_parse()` IPv4 address-with-port parsing in `subsys/net/ip/utils.c`

## Summary
Severity: High
Advisory: CVE-2026-10666
Aliases: GHSA-532c-7g7f-jhmh
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-12
Source: https://osv.dev/vulnerability/CVE-2026-10666
Type: osv

## Details
parse_ipv4() in subsys/net/ip/utils.c (reached via net_ipaddr_parse() for strings of the form "a.b.c.d:port") copies the port substring into a fixed 17-byte stack buffer (char ipaddr[NET_IPV4_ADDR_LEN + 1]) using a length of str_len - end - 1, where str_len is the full, unbounded input length and end is only the (<=15-byte) offset of the ':' delimiter. Because the destination size is never consulted, a crafted address string with a long suffix after the colon (e.g. "1.2.3.4:" followed by hundreds of bytes) causes an out-of-bounds stack write whose length and contents are fully attacker-controlled (memcpy of the suffix plus a trailing NUL), enabling memory corruption and at minimum a denial of service, and potentially control-flow hijack. The parser is reached from the standard socket API (zsock_getaddrinfo / literal-address resolution), DNS server-string configuration, and the eswifi Wi-Fi co-processor DNS-response path, so an application that resolves a network-influenced address string is exposed. The bug was introduced when the parser was added (Zephyr v1.9.0) and shipped in all releases through v4.4.0. The fix removes the unbounded copy and validates the port length before copying into a small dedicated buffer. Note: the equivalent IPv6 "[addr]:port" path in parse_ipv6() retains the same unbounded copy at this commit and remains a separate, still-reachable instance of the defect.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10666.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-532c-7g7f-jhmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-10666
- https://github.com/zephyrproject-rtos/zephyr/commit/1c8d19a51f9a3c1be6de53854c8ad8c2720a0f48
- https://github.com/zephyrproject-rtos/zephyr/commit/6e119a636a57be449ea21e73cad762ebc6f5ff7a
- https://github.com/zephyrproject-rtos/zephyr

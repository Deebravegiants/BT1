# [H] CVE-2025-50681

## Summary
Severity: High
Advisory: CVE-2025-50681
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-50681
Type: osv

## Details
igmpproxy 0.4 before commit 2b30c36 allows remote attackers to cause a denial of service (application crash) via a crafted IGMPv3 membership report packet with a malicious source address. Due to insufficient validation in the `recv_igmp()` function in src/igmpproxy.c, an invalid group record type can trigger a NULL pointer dereference when logging the address using `inet_fmtsrc()`. This vulnerability can be exploited by sending malformed multicast traffic to a host running igmpproxy, leading to a crash. igmpproxy is used in various embedded networking environments and consumer-grade IoT devices (such as home routers and media gateways) to handle multicast traffic for IPTV and other streaming services. Affected devices that rely on unpatched versions of igmpproxy may be vulnerable to remote denial-of-service attacks across a LAN .

## References
- https://gist.github.com/miora-sora/dac1612d16c45c2aedb8605478adc28f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50681.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50681
- https://github.com/pali/igmpproxy/issues/97
- https://github.com/younix/igmpproxy/commit/2b30c36e6ab5b21defb76ec6458ab7687984484c

# [H] BusyBox DHCPv6 Client Heap Buffer Overflow via DNS_SERVERS

## Summary
Severity: High
Advisory: CVE-2026-29004
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-29004
Type: osv

## Details
BusyBox before commit 42202bf contains a heap buffer overflow vulnerability in the DHCPv6 client (udhcpc6) DNS_SERVERS option handler in networking/udhcp/d6_dhcpc.c that allows network-adjacent attackers to trigger memory corruption by sending a crafted DHCPv6 response with a malformed D6_OPT_DNS_SERVERS option. Attackers can exploit incorrect heap buffer allocation calculations in the option_to_env() function to cause denial of service or achieve arbitrary code execution on embedded systems without heap hardening.

## References
- https://busybox.net/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-29004.json
- https://access.redhat.com/errata/RHSA-2026:30652
- https://access.redhat.com/security/cve/CVE-2026-29004
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29004
- https://www.vulncheck.com/advisories/busybox-dhcpv6-client-heap-buffer-overflow-via-dns-servers
- https://bugzilla.redhat.com/show_bug.cgi?id=2466526
- https://github.com/vda-linux/busybox_mirror/commit/42202bfb1e6ac51fa995beda8be4d7b654aeee2a
- https://github.com/vda-linux/busybox_mirror/commit/d368f3f7836d1c2484c8f839316e5c93e76d4409
- https://y637f9qq2x.com/posts/busybox-dhcpv6-heap-overflow/

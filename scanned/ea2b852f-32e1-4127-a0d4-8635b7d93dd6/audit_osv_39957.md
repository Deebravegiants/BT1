# [C] radvdump's Route Information Option Parser has a Stack Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2026-48715
Aliases: GHSA-52px-gh9p-m379
CVSS: 9.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-48715
Type: osv

## Details
radvd is a router advertisement daemon for IPv6. Prior to version 2.21, the `radvdump` utility shipped with radvd contains a stack buffer overflow in the Route Information option parser. When processing a crafted ICMPv6 Router Advertisement, `print_ff()` copies up to 2032 bytes from attacker-controlled packet data into a 16-byte `struct in6_addr` on the stack, overflowing by up to 2016 bytes. Note that the main `radvd` daemon is not affected by the vulnerability. Version 2.21 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48715.json
- https://github.com/radvd-project/radvd/security/advisories/GHSA-52px-gh9p-m379
- https://nvd.nist.gov/vuln/detail/CVE-2026-48715
- https://github.com/radvd-project/radvd/commit/068bde13e3fd6a5fcdb6859e6a2acd293a325dc5

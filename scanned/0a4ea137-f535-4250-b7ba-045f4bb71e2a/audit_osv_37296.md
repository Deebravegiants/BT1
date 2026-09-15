# [C] OpenWrt Project has Stack-based Buffer Overflow in DNS PTR Query

## Summary
Severity: Critical
Advisory: CVE-2026-30871
Aliases: GHSA-7c3j-f7w2-p8f6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-30871
Type: osv

## Details
OpenWrt Project is a Linux operating system targeting embedded devices. In versions prior to 24.10.6 and 25.12.1, the mdns daemon has a Stack-based Buffer Overflow vulnerability in the parse_question function. The issue is  triggered by PTR queries for reverse DNS domains (.in-addr.arpa and .ip6.arpa). DNS packets received on UDP port 5353 are expanded by dn_expand into an 8096-byte global buffer (name_buffer), which is then copied via an unbounded strcpy into a fixed 256-byte stack buffer when handling TYPE_PTR queries. The overflow is possible because dn_expand converts non-printable ASCII bytes (e.g., 0x01) into multi-character octal representations (e.g., \001), significantly inflating the expanded name beyond the stack buffer's capacity. A crafted DNS packet can exploit this expansion behavior to overflow the stack buffer, making the vulnerability reachable through normal multicast DNS packet processing. This issue has been fixed in versions 24.10.6 and 25.12.1.

## References
- https://github.com/openwrt/openwrt/releases/tag/v24.10.6
- https://github.com/openwrt/openwrt/releases/tag/v25.12.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30871.json
- https://github.com/openwrt/openwrt/security/advisories/GHSA-7c3j-f7w2-p8f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-30871

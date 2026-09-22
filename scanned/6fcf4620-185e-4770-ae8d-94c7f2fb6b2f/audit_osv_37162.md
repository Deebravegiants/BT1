# [M] U-Boot 2026.04-rc3 Integer Underflow DoS via tcp_rx_state_machine()

## Summary
Severity: Medium
Advisory: CVE-2026-29008
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-29008
Type: osv

## Details
U-Boot through 2026.04-rc3 contains an integer underflow vulnerability in the tcp_rx_state_machine() function (net/tcp.c) that allows a network-adjacent attacker to crash the bootloader by sending a malformed TCP SYN+ACK packet with a manipulated data offset field causing payload_len to become negative. When the TCP_SYN_SENT handler calls tcp_rx_user_data() without invoking tcp_seg_in_wnd() validation, the negative payload_len is implicitly converted to a large unsigned integer (e.g., 0xFFFFFFD8) and passed to memcpy() in store_block(), causing an immediate crash that prevents device boot and may enable memory corruption when CONFIG_LMB is disabled.

## References
- https://u-boot.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29008.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29008
- https://www.vulncheck.com/advisories/u-boot-rc3-integer-underflow-dos-via-tcp-rx-state-machine
- https://lists.denx.de/pipermail/u-boot/2026-May/617853.html
- https://github.com/u-boot/u-boot
- https://y637f9qq2x.com/posts/u-boot-tcp-nfs-vulns/

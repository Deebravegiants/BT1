# [M] pam_authnft: Heap buffer overflow in NETLINK_SOCK_DIAG reply walker

## Summary
Severity: Medium
Advisory: CVE-2026-43916
Aliases: GHSA-5jj5-hm34-78vh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43916
Type: osv

## Details
pam_authnft is a PAM session module binding nftables firewall rules to authenticated sessions via cgroupv2 inodes. Prior to 0.2.0-alpha, a heap buffer over-read in peer_lookup_tcp (src/peer_lookup.c:134, prior to the fix) allowed a crafted NETLINK_SOCK_DIAG reply to slip past the message-size check, then dereference past the end of the allocation. This vulnerability is fixed in 0.2.0-alpha.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43916.json
- https://github.com/identd-ng/pam_authnft/security/advisories/GHSA-5jj5-hm34-78vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-43916
- https://github.com/identd-ng/pam_authnft/pull/10

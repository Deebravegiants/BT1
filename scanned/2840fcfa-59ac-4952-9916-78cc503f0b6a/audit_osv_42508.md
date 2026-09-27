# [H] sctp: fix auth_chunk_list capacity check in sctp_auth_ep_add_chunkid

## Summary
Severity: High
Advisory: CVE-2026-68320
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68320
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix auth_chunk_list capacity check in sctp_auth_ep_add_chunkid

sctp_auth_ep_add_chunkid() uses SCTP_NUM_CHUNK_TYPES (20) as the
capacity limit for ep->auth_chunk_list, allowing it to hold up to
20 chunk entries (param_hdr.length up to 24). However, the copy
destination asoc->c.auth_chunks in struct sctp_cookie is only
SCTP_AUTH_MAX_CHUNKS (16) entries (20 bytes). When more than 16
chunks are added, sctp_association_init() memcpy overflows the
destination by up to 4 bytes.

Fix by using SCTP_AUTH_MAX_CHUNKS as the capacity limit, matching
the destination capacity.

## References
- https://git.kernel.org/stable/c/11092d79eb2b7c0068382f72fc2416d1786bb2e0
- https://git.kernel.org/stable/c/3d22a7da2e264f407c729f33a0a346ff76108bc6
- https://git.kernel.org/stable/c/54bb4c03fa17cdcb157c26c33e60a78cf32960f5
- https://git.kernel.org/stable/c/5a365f1e423444c5da7eb689a8661633dad43e48
- https://git.kernel.org/stable/c/6837c1c19a259518974cbc5a52017646e3906564
- https://git.kernel.org/stable/c/886e28e14ab655012779016d251fef53d103aa12
- https://git.kernel.org/stable/c/b6ea3dda09eb4d5caf7bbc00f857688cf9e98255
- https://git.kernel.org/stable/c/ff04b26794a16a8a879eb4fd2c02c2d6b03850e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68320.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68320
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] libceph: replace overzealous BUG_ON in osdmap_apply_incremental()

## Summary
Severity: High
Advisory: CVE-2026-22990
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-22990
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: replace overzealous BUG_ON in osdmap_apply_incremental()

If the osdmap is (maliciously) corrupted such that the incremental
osdmap epoch is different from what is expected, there is no need to
BUG.  Instead, just declare the incremental osdmap to be invalid.

## References
- https://git.kernel.org/stable/c/4b106fbb1c7b841cd402abd83eb2447164c799ea
- https://git.kernel.org/stable/c/6348d70af847b79805374fe628d3809a63fd7df3
- https://git.kernel.org/stable/c/6afd2a4213524bc742b709599a3663aeaf77193c
- https://git.kernel.org/stable/c/6c6cec3db3b418c4fdf815731bc39e46dff75e1b
- https://git.kernel.org/stable/c/9aa0b0c14cefece078286d78b97d4c09685e372d
- https://git.kernel.org/stable/c/d3613770e2677683e65d062da5e31f48c409abe9
- https://git.kernel.org/stable/c/e00c3f71b5cf75681dbd74ee3f982a99cb690c2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22990.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

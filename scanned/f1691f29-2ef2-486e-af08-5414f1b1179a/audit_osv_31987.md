# [H] ocfs2: validate l_tree_depth to avoid out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2025-22079
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22079
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: validate l_tree_depth to avoid out-of-bounds access

The l_tree_depth field is 16-bit (__le16), but the actual maximum depth is
limited to OCFS2_MAX_PATH_DEPTH.

Add a check to prevent out-of-bounds access if l_tree_depth has an invalid
value, which may occur when reading from a corrupted mounted disk [1].

## References
- https://git.kernel.org/stable/c/11e24802e73362aa2948ee16b8fb4e32635d5b2a
- https://git.kernel.org/stable/c/17c99ab3db2ba74096d36c69daa6e784e98fc0b8
- https://git.kernel.org/stable/c/3d012ba4404a0bb517658699ba85e6abda386dc3
- https://git.kernel.org/stable/c/49d2a2ea9d30991bae82107f9523915b91637683
- https://git.kernel.org/stable/c/538ed8b049ef801a86c543433e5061a91cc106e3
- https://git.kernel.org/stable/c/a406aff8c05115119127c962cbbbbd202e1973ef
- https://git.kernel.org/stable/c/b942f88fe7d2d789e51c5c30a675fa1c126f5a6d
- https://git.kernel.org/stable/c/e95d97c9c8cd0c239b7b59c79be0f6a9dcf7905c
- https://git.kernel.org/stable/c/ef34840bda333fe99bafbd2d73b70ceaaf9eba66
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22079.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22079
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

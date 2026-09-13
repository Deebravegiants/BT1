# [M] Kernel: nf_tables: pointer math issue in nft_byteorder_eval()

## Summary
Severity: Medium
Advisory: CVE-2024-0607
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2024-0607
Type: osv

## Details
A flaw was found in the Netfilter subsystem in the Linux kernel. The issue is in the nft_byteorder_eval() function, where the code iterates through a loop and writes to the `dst` array. On each iteration, 8 bytes are written, but `dst` is an array of u32, so each element only has space for 4 bytes. That means every iteration overwrites part of the previous element corrupting this array of u32. This flaw allows a local user to cause a denial of service or potentially break NetFilter functionality.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://access.redhat.com/security/cve/CVE-2024-0607
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0607.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0607
- https://bugzilla.redhat.com/show_bug.cgi?id=2258635
- https://github.com/torvalds/linux/commit/c301f0981fdd3fd1ffac6836b423c4d7a8e0eb63

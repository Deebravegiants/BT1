# [H] net: phy: micrel: Fix potential null pointer dereference

## Summary
Severity: High
Advisory: CVE-2024-35891
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35891
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: micrel: Fix potential null pointer dereference

In lan8814_get_sig_rx() and lan8814_get_sig_tx() ptp_parse_header() may
return NULL as ptp_header due to abnormal packet type or corrupted packet.
Fix this bug by adding ptp_header check.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/10608161696c2768f53426642f78a42bcaaa53e8
- https://git.kernel.org/stable/c/49767b0df276f12e3e7184601e09ee7430e252dc
- https://git.kernel.org/stable/c/95c1016a2d92c4c28a9d1b6d09859c00b19c0ea4
- https://git.kernel.org/stable/c/96c155943a703f0655c0c4cab540f67055960e91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35891.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35891
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] net: fec: don't save PTP state if PTP is unsupported

## Summary
Severity: Medium
Advisory: CVE-2024-50097
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50097
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.55 <6.6.57, >=6.11.3 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fec: don't save PTP state if PTP is unsupported

Some platforms (such as i.MX25 and i.MX27) do not support PTP, so on
these platforms fec_ptp_init() is not called and the related members
in fep are not initialized. However, fec_ptp_save_state() is called
unconditionally, which causes the kernel to panic. Therefore, add a
condition so that fec_ptp_save_state() is not called if PTP is not
supported.

## References
- https://git.kernel.org/stable/c/3192e8d4a1ef9fc9bd7a59cdce51543367e5edd6
- https://git.kernel.org/stable/c/6be063071a457767ee229db13f019c2ec03bfe44
- https://git.kernel.org/stable/c/7745e14f4c036ce94a5eb05d06e49b0d84b306f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50097.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50097
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] usb: typec: qcom-pmic: init value of hdr_len/txbuf_len earlier

## Summary
Severity: Medium
Advisory: CVE-2024-53083
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53083
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: qcom-pmic: init value of hdr_len/txbuf_len earlier

If the read of USB_PDPHY_RX_ACKNOWLEDGE_REG failed, then hdr_len and
txbuf_len are uninitialized. This commit stops to print uninitialized
value and misleading/false data.

## References
- https://git.kernel.org/stable/c/029778a4fd2c90c2e76a902b797c2348a722f1b8
- https://git.kernel.org/stable/c/35925e2b7b404cad3db857434d3312b892b55432
- https://git.kernel.org/stable/c/74d8cee747b37cd9f5ca631f678e66e7f40f2b5f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53083.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

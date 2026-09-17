# [H] Bluetooth: HCI: Remove HCI_AMP support

## Summary
Severity: High
Advisory: CVE-2024-38620
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2024-38620
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <6.1.184, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: HCI: Remove HCI_AMP support

Since BT_HS has been remove HCI_AMP controllers no longer has any use so
remove it along with the capability of creating AMP controllers.

Since we no longer need to differentiate between AMP and Primary
controllers, as only HCI_PRIMARY is left, this also remove
hdev->dev_type altogether.

## References
- https://git.kernel.org/stable/c/5af2e235b0d5b797e9531a00c50058319130e156
- https://git.kernel.org/stable/c/84a4bb6548a29326564f0e659fb8064503ecc1c7
- https://git.kernel.org/stable/c/9e6cf0eccfe15b67bf9773ecd101162dfdfed5e2
- https://git.kernel.org/stable/c/af1d425b6dc67cd67809f835dd7afb6be4d43e03
- https://git.kernel.org/stable/c/d3c7b012d912b31ad23b9349c0e499d6dddd48ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38620.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38620
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] Bluetooth: btusb: mediatek: Fix double free of skb in coredump

## Summary
Severity: High
Advisory: CVE-2024-35856
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35856
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btusb: mediatek: Fix double free of skb in coredump

hci_devcd_append() would free the skb on error so the caller don't
have to free it again otherwise it would cause the double free of skb.

Reported-by : Dan Carpenter <dan.carpenter@linaro.org>

## References
- https://git.kernel.org/stable/c/18bdb386a1a30e7a3d7732a98e45e69cf6b5710d
- https://git.kernel.org/stable/c/80dfef128cb9f1b1ef67c0fe8c8deb4ea7ad30c1
- https://git.kernel.org/stable/c/e20093c741d8da9f6390dd45d75b779861547035
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35856.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35856
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

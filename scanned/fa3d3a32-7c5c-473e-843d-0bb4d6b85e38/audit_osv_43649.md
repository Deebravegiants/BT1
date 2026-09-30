# [H] Bluetooth: hci_sync: hold conn in hci_past_sync() callback

## Summary
Severity: High
Advisory: CVE-2026-74528
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74528
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: hold conn in hci_past_sync() callback

Avoids giving freed pointers to hci_conn_valid(), which kmalloc may have
reused.

Hold refcount to avoid that.

## References
- https://git.kernel.org/stable/c/abf9753edf3f88282c44a605f3945d8d4f8dd86c
- https://git.kernel.org/stable/c/e6792adef614b389141b142e30ee549e4a47dd7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74528.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74528
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

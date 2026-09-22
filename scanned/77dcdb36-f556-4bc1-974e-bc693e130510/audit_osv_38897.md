# [H] Bluetooth: hci_conn: fix potential UAF in set_cig_params_sync

## Summary
Severity: High
Advisory: CVE-2026-43019
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43019
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.143, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_conn: fix potential UAF in set_cig_params_sync

hci_conn lookup and field access must be covered by hdev lock in
set_cig_params_sync, otherwise it's possible it is freed concurrently.

Take hdev lock to prevent hci_conn from being deleted or modified
concurrently.  Just RCU lock is not suitable here, as we also want to
avoid "tearing" in the configuration.

## References
- https://git.kernel.org/stable/c/66d432e9b45bae7881ffcdb12cd8fd0bf254ef02
- https://git.kernel.org/stable/c/7502c1cf303b69f71d085f5ff7251b0e1b0f09df
- https://git.kernel.org/stable/c/7d568fede8eac91161a60b710aa920abe9b0fb9f
- https://git.kernel.org/stable/c/a2639a7f0f5bf7d73f337f8f077c19415c62ed2c
- https://git.kernel.org/stable/c/bad65b4b0a96139f023eadc28a33125963208449
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43019.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

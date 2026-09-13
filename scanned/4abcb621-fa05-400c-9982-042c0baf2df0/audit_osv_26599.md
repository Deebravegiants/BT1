# [H] Bluetooth: Fix potential use-after-free when clear keys

## Summary
Severity: High
Advisory: CVE-2023-53386
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53386
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Fix potential use-after-free when clear keys

Similar to commit c5d2b6fa26b5 ("Bluetooth: Fix use-after-free in
hci_remove_ltk/hci_remove_irk"). We can not access k after kfree_rcu()
call.

## References
- https://git.kernel.org/stable/c/35cc42f04bc49f0656f6840cb7451b3df6049649
- https://git.kernel.org/stable/c/3673952cf0c6cf81b06c66a0b788abeeb02ff3ae
- https://git.kernel.org/stable/c/942d8cefb022f384d5424f8b90c7878f3f93726f
- https://git.kernel.org/stable/c/94617b736c25091b60e514e2e7aeafcbbee6b700
- https://git.kernel.org/stable/c/da19f35868dfbecfff4f81166c054d2656cb1be4
- https://git.kernel.org/stable/c/e87da6a0ac6e631454e7da53a76aa9fe44aaa5dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53386.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53386
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

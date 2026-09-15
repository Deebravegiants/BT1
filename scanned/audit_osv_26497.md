# [M] wifi: iwl3945: Add missing check for create_singlethread_workqueue

## Summary
Severity: Medium
Advisory: CVE-2023-53277
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53277
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwl3945: Add missing check for create_singlethread_workqueue

Add the check for the return value of the create_singlethread_workqueue
in order to avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/17e07d6587c55015956862ef3b101fd45fa49fbc
- https://git.kernel.org/stable/c/1fdeb8b9f29dfd64805bb49475ac7566a3cb06cb
- https://git.kernel.org/stable/c/2f80b3ff92514ebd227e5c55d3d1e480401b02b7
- https://git.kernel.org/stable/c/34f611204ae589bd5c494b10b41fb13436bd3c3f
- https://git.kernel.org/stable/c/3ae2fc4de12686f3fe695824169c1272c9f798f7
- https://git.kernel.org/stable/c/505c74c4c0b1c5bcaa98a93b3087c268156070f1
- https://git.kernel.org/stable/c/7e594abc0424e4f8c2385f11aefeaadcfc507aa5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53277.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

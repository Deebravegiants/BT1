# [H] apparmor: fix refcount leak when updating the sk_ctx

## Summary
Severity: High
Advisory: CVE-2026-72461
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72461
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix refcount leak when updating the sk_ctx

Currently update_sk_ctx() transfers the plabel reference, unfortunately
it is also unconditionally put in the caller. Ideally we would make
the caller conditionally put the reference based on whether it was
transferred but for now just fix the bug by getting a reference.

## References
- https://git.kernel.org/stable/c/045dbe89ac31709abd73390d0805d52fece7ef39
- https://git.kernel.org/stable/c/6d25e7b47616cb2db43351210929c8f19dc305a3
- https://git.kernel.org/stable/c/b8642f1478982a97ca2eb59f70f631a9de42ae11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72461.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

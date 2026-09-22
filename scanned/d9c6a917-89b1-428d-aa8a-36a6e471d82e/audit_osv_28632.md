# [H] x86/fpu: Keep xfd_state in sync with MSR_IA32_XFD

## Summary
Severity: High
Advisory: CVE-2024-35801
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35801
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/fpu: Keep xfd_state in sync with MSR_IA32_XFD

Commit 672365477ae8 ("x86/fpu: Update XFD state where required") and
commit 8bf26758ca96 ("x86/fpu: Add XFD state to fpstate") introduced a
per CPU variable xfd_state to keep the MSR_IA32_XFD value cached, in
order to avoid unnecessary writes to the MSR.

On CPU hotplug MSR_IA32_XFD is reset to the init_fpstate.xfd, which
wipes out any stale state. But the per CPU cached xfd value is not
reset, which brings them out of sync.

As a consequence a subsequent xfd_update_state() might fail to update
the MSR which in turn can result in XRSTOR raising a #NM in kernel
space, which crashes the kernel.

To fix this, introduce xfd_set_state() to write xfd_state together
with MSR_IA32_XFD, and use it in all places that set MSR_IA32_XFD.

## References
- https://git.kernel.org/stable/c/10e4b5166df9ff7a2d5316138ca668b42d004422
- https://git.kernel.org/stable/c/1acbca933313aa866e39996904c9aca4d435c4cd
- https://git.kernel.org/stable/c/21c7c00dae55cb0e3810d5f9506b58f68475d41d
- https://git.kernel.org/stable/c/92b0f04e937665bde5768f3fcc622dcce44413d8
- https://git.kernel.org/stable/c/b61e3b7055ac6edee4be071c52f48c26472d2624
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35801.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

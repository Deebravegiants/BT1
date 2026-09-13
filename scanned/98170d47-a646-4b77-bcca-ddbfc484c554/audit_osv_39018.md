# [H] drm/amdgpu: Fix use-after-free race in VM acquire

## Summary
Severity: High
Advisory: CVE-2026-43370
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43370
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix use-after-free race in VM acquire

Replace non-atomic vm->process_info assignment with cmpxchg()
to prevent race when parent/child processes sharing a drm_file
both try to acquire the same VM after fork().

(cherry picked from commit c7c573275ec20db05be769288a3e3bb2250ec618)

## References
- https://git.kernel.org/stable/c/2c1030f2e84885cc58bffef6af67d5b9d2e7098f
- https://git.kernel.org/stable/c/46d309996bd9251792d7dafdbaf615cf202b4447
- https://git.kernel.org/stable/c/7885eb335d8f9e9942925d57e300a85e3f82ded4
- https://git.kernel.org/stable/c/904025fa8bba1d028adade33346372b4ac1a9249
- https://git.kernel.org/stable/c/94b7782d0c8024f5b88454241c8d4777076c3786
- https://git.kernel.org/stable/c/ae87aea330c24f462fc7058ed543ba8bc6798447
- https://git.kernel.org/stable/c/c658c1c85ec235b7ecfbf8dbfee385b1332088f4
- https://git.kernel.org/stable/c/e61e355cbe49e585097eee28c15b862bfb1c0668
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43370.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43370
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

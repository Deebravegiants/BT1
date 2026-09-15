# [M] ALSA: control: Avoid WARN() for symlink errors

## Summary
Severity: Medium
Advisory: CVE-2024-56657
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56657
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: control: Avoid WARN() for symlink errors

Using WARN() for showing the error of symlink creations don't give
more information than telling that something goes wrong, since the
usual code path is a lregister callback from each control element
creation.  More badly, the use of WARN() rather confuses fuzzer as if
it were serious issues.

This patch downgrades the warning messages to use the normal dev_err()
instead of WARN().  For making it clearer, add the function name to
the prefix, too.

## References
- https://git.kernel.org/stable/c/365ee29e559269cbb2108c4cc05dd8e262b4e84e
- https://git.kernel.org/stable/c/36c0764474b637bbee498806485bed524cad486b
- https://git.kernel.org/stable/c/4e5a92a7223c83c1f5f2db6cd010ac9347948972
- https://git.kernel.org/stable/c/b2e538a9827dd04ab5273bf4be8eb2edb84357b0
- https://git.kernel.org/stable/c/d5a1ca7b59804d6779644001a878ed925a4688ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56657.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56657
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

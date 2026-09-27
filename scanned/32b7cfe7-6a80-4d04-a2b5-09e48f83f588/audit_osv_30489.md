# [M] firmware: qcom: scm: fix a NULL-pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2024-53069
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53069
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: qcom: scm: fix a NULL-pointer dereference

Some SCM calls can be invoked with __scm being NULL (the driver may not
have been and will not be probed as there's no SCM entry in device-tree).
Make sure we don't dereference a NULL pointer.

## References
- https://git.kernel.org/stable/c/3d36e2b1d803f0d1cc674115d295a8f20ddb9268
- https://git.kernel.org/stable/c/ca61d6836e6f4442a77762e1074d2706a2a6e578
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

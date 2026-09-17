# [M] firmware: qcom: qseecom: fix memory leaks in error paths

## Summary
Severity: Medium
Advisory: CVE-2023-52684
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52684
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: qcom: qseecom: fix memory leaks in error paths

Fix instances of returning error codes directly instead of jumping to
the relevant labels where memory allocated for the SCM calls would be
freed.

## References
- https://git.kernel.org/stable/c/6c57d7b593c4a4e60db65d5ce0fe1d9f79ccbe9b
- https://git.kernel.org/stable/c/85fdbf6840455be64eac16bdfe0df3368ee3d0f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52684.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52684
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

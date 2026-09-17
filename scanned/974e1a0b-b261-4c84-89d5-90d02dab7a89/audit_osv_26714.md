# [H] Input: exc3000 - properly stop timer on shutdown

## Summary
Severity: High
Advisory: CVE-2023-53651
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53651
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.20, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: exc3000 - properly stop timer on shutdown

We need to stop the timer on driver unbind or probe failures, otherwise
we get UAF/Oops.

## References
- https://git.kernel.org/stable/c/526a177ac6353d65057eadb5d6edafc168f64484
- https://git.kernel.org/stable/c/79c81d137d36f9635bbcbc3916c0cccb418a61dd
- https://git.kernel.org/stable/c/bee57c20fc0ca5ef9b9a53a0335eab2ac9e9cae1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53651.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53651
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

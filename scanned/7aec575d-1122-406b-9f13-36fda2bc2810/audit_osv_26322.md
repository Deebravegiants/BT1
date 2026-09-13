# [M] media: vidtv: psi: Add check for kstrdup

## Summary
Severity: Medium
Advisory: CVE-2023-52844
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52844
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vidtv: psi: Add check for kstrdup

Add check for the return value of kstrdup() and return the error
if it fails in order to avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/3387490c89b10aeb4e71d78b65dbc9ba4b2385b9
- https://git.kernel.org/stable/c/5c26aae3723965c291c65dd2ecad6a3240d422b0
- https://git.kernel.org/stable/c/5cfcc8de7d733a1137b86954cc28ce99972311ad
- https://git.kernel.org/stable/c/76a2c5df6ca8bd8ada45e953b8c72b746f42918d
- https://git.kernel.org/stable/c/a51335704a3f90eaf23a6864faefca34b382490a
- https://git.kernel.org/stable/c/d17269fb9161995303985ab2fe6f16cfb72152f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52844.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52844
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

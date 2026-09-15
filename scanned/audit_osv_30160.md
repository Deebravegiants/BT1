# [H] net: pse-pd: Fix out of bound for loop

## Summary
Severity: High
Advisory: CVE-2024-50129
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50129
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: pse-pd: Fix out of bound for loop

Adjust the loop limit to prevent out-of-bounds access when iterating over
PI structures. The loop should not reach the index pcdev->nr_lines since
we allocate exactly pcdev->nr_lines number of PI structures. This fix
ensures proper bounds are maintained during iterations.

## References
- https://git.kernel.org/stable/c/50ea68146d82f34b3ad80d8290ef8222136dedd7
- https://git.kernel.org/stable/c/f2767a41959e60763949c73ee180e40c686e807e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50129.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

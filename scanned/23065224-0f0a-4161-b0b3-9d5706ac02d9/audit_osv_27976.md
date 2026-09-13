# [H] drm/amd/display: fix incorrect mpc_combine array size

## Summary
Severity: High
Advisory: CVE-2024-26914
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26914
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: fix incorrect mpc_combine array size

[why]
MAX_SURFACES is per stream, while MAX_PLANES is per asic. The
mpc_combine is an array that records all the planes per asic. Therefore
MAX_PLANES should be used as the array size. Using MAX_SURFACES causes
array overflow when there are more than 3 planes.

[how]
Use the MAX_PLANES for the mpc_combine array size.

## References
- https://git.kernel.org/stable/c/0bd8ef618a42d7e6ea3f701065264e15678025e3
- https://git.kernel.org/stable/c/39079fe8e660851abbafa90cd55cbf029210661f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26914.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

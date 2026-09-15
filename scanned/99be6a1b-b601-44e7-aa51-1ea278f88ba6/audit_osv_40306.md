# [H] xfrm: ipcomp: Free destination pages on acomp errors

## Summary
Severity: High
Advisory: CVE-2026-52932
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52932
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: ipcomp: Free destination pages on acomp errors

Move the out_free_req label up by a couple of lines so that the
allocated dst SG list gets freed on error as well as success.

## References
- https://git.kernel.org/stable/c/7dbac7680eb629b3b4dc7e98c34f943b8814c0c8
- https://git.kernel.org/stable/c/b30aa173c3809f6af4c83a86099be1be19aa48eb
- https://git.kernel.org/stable/c/dc6dcba80d72a27ab61831ad3d253316e0c9b9d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52932.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [M] Git's `git apply` overwriting paths outside the working tree

## Summary
Severity: Medium
Advisory: CVE-2023-23946
Aliases: GHSA-r87m-v37r-cwfh
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-23946
Type: osv

## Details
Git, a revision control system, is vulnerable to path traversal prior to versions 2.39.2, 2.38.4, 2.37.6, 2.36.5, 2.35.7, 2.34.7, 2.33.7, 2.32.6, 2.31.7, and 2.30.8. By feeding a crafted input to `git apply`, a path outside the working tree can be overwritten as the user who is running `git apply`. A fix has been prepared and will appear in v2.39.2, v2.38.4, v2.37.6, v2.36.5, v2.35.7, v2.34.7, v2.33.7, v2.32.6, v2.31.7, and v2.30.8. As a workaround, use `git apply --stat` to inspect a patch before applying; avoid applying one that creates a symbolic link and then creates a file beyond the symbolic link.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23946.json
- https://github.com/git/git/security/advisories/GHSA-r87m-v37r-cwfh
- https://nvd.nist.gov/vuln/detail/CVE-2023-23946
- https://security.gentoo.org/glsa/202312-15
- https://github.com/git/git/commit/c867e4fa180bec4750e9b54eb10f459030dbebfd

# [H] fs/ntfs3: Add a check for attr_names and oatbl

## Summary
Severity: High
Advisory: CVE-2024-41018
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41018
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.43, >=6.7.0 <6.9.12, >=6.8.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Add a check for attr_names and oatbl

Added out-of-bound checking for *ane (ATTR_NAME_ENTRY).

## References
- https://git.kernel.org/stable/c/702d4930eb06dcfda85a2fa67e8a1a27bfa2a845
- https://git.kernel.org/stable/c/9b71f820f7168f1eab8378c80c7ea8a022a475bc
- https://git.kernel.org/stable/c/c114d2b88f8b226d4b2acf5a1ba0412cde6c31dd
- https://git.kernel.org/stable/c/f3124d51e4e7b56a732419d8dc270e807252334f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41018.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

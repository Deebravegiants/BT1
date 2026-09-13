# [M] cifs: fix potential memory leaks in session setup

## Summary
Severity: Medium
Advisory: CVE-2023-53008
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53008
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix potential memory leaks in session setup

Make sure to free cifs_ses::auth_key.response before allocating it as
we might end up leaking memory in reconnect or mounting.

## References
- https://git.kernel.org/stable/c/2fe58d977ee05da5bb89ef5dc4f5bf2dc15db46f
- https://git.kernel.org/stable/c/893d45394dbe4b5cbf3723c19e2ccc8b93a6ac9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53008.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53008
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

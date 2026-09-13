# [M] ceph: properly put ceph_string reference after async create attempt

## Summary
Severity: Medium
Advisory: CVE-2022-48767
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48767
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.96, >=5.11.0 <5.15.19, >=5.16.0 <5.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: properly put ceph_string reference after async create attempt

The reference acquired by try_prep_async_create is currently leaked.
Ensure we put it.

## References
- https://git.kernel.org/stable/c/36d433ae3242aa714176378850e6d1a5a3e78f18
- https://git.kernel.org/stable/c/932a9b5870d38b87ba0a9923c804b1af7d3605b9
- https://git.kernel.org/stable/c/a0c22e970cd78b81c94691e6cb09713e8074d580
- https://git.kernel.org/stable/c/e7be12ca7d3947765b0d7c1c7e0537e748da993a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48767.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48767
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

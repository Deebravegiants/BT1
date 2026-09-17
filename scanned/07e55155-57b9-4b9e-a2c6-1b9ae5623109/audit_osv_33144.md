# [H] io_uring/memmap: cast nr_pages to size_t before shifting

## Summary
Severity: High
Advisory: CVE-2025-39793
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/CVE-2025-39793
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/memmap: cast nr_pages to size_t before shifting

If the allocated size exceeds UINT_MAX, then it's necessary to cast
the mr->nr_pages value to size_t to prevent it from overflowing. In
practice this isn't much of a concern as the required memory size will
have been validated upfront, and accounted to the user. And > 4GB sizes
will be necessary to make the lack of a cast a problem, which greatly
exceeds normal user locked_vm settings that are generally in the kb to
mb range. However, if root is used, then accounting isn't done, and
then it's possible to hit this issue.

## References
- https://git.kernel.org/stable/c/33503c083fda048c77903460ac0429e1e2c0e341
- https://git.kernel.org/stable/c/a69a9b53c54e2d33e2a5b1ea4a9a71fd01c6cf3a
- https://git.kernel.org/stable/c/c6a2706e08b8a1b2d3740161c0977d38e596c1ee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39793.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39793
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

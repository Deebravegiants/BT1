# [H] memfd: deny writeable mappings when implying SEAL_WRITE

## Summary
Severity: High
Advisory: CVE-2026-63952
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63952
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

memfd: deny writeable mappings when implying SEAL_WRITE

When SEAL_EXEC is added, SEAL_WRITE is implied to make W^X.  But the
implied seal is set after the check that makes sure the memfd can not have
any writable mappings.  This means one can use SEAL_EXEC to apply
SEAL_WRITE while having writeable mappings.

This breaks the contract that SEAL_WRITE provides and can be used by an
attacker to pass a memfd that appears to be write sealed but can still be
modified arbitrarily.

Fix this by adding the implied seals before the call for
mapping_deny_writable() is done.

## References
- https://git.kernel.org/stable/c/0995d1f79aed8ccbf62056189dd53fd19726ea08
- https://git.kernel.org/stable/c/3b041514cb6eae45869b020f743c14d983363222
- https://git.kernel.org/stable/c/3be2a24f7f72ad7321ed6ad1715b956a4527bcf4
- https://git.kernel.org/stable/c/555702282d4536a865dfffb1cd4f6028f196e7e8
- https://git.kernel.org/stable/c/b3f4f82d1315f1439059a83d1c22c51a5b43d99e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63952.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63952
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

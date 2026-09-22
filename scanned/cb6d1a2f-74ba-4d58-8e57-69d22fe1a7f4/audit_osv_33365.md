# [H] sctp: Fix MAC comparison to be constant-time

## Summary
Severity: High
Advisory: CVE-2025-40204
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40204
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: Fix MAC comparison to be constant-time

To prevent timing attacks, MACs need to be compared in constant time.
Use the appropriate helper function for this.

## References
- https://git.kernel.org/stable/c/0b32ff285ff6f6f1ac1d9495787ccce8837d6405
- https://git.kernel.org/stable/c/0e8b8c326c2a6de4d837b1bb034ea704f4690d77
- https://git.kernel.org/stable/c/1cd60e0d0fb8f0e62ec4499138afce6342dc9d4c
- https://git.kernel.org/stable/c/8019b3699289fce3f10b63f98601db97b8d105b0
- https://git.kernel.org/stable/c/9c05d44ec24126fc283835b68f82dba3ae985209
- https://git.kernel.org/stable/c/b93fa8dc521d00d2d44bf034fb90e0d79b036617
- https://git.kernel.org/stable/c/dd91c79e4f58fbe2898dac84858033700e0e99fb
- https://git.kernel.org/stable/c/ed3044b9c810c5c24eb2830053fbfe5fd134c5d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40204.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40204
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

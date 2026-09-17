# [H] dm-integrity: fix a bug if the bio is out of limits

## Summary
Severity: High
Advisory: CVE-2026-72100
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72100
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-integrity: fix a bug if the bio is out of limits

If dm_integrity_check_limits fails, the code would exit with
DM_MAPIO_KILL. However, the range would be already locked at this point,
and it wouldn't be unlocked, resulting in a deadlock. Let's move the
limit check up, so that when it exits, no resources are leaked.

## References
- https://git.kernel.org/stable/c/3d1afaa074622859678b1a1e7c1b9c0af74c89b0
- https://git.kernel.org/stable/c/5a266764fadaff8b5c1fe37a186ebf9b09cb953e
- https://git.kernel.org/stable/c/aa5113e7155f4ea81d2c0303ab5cb272d4b32627
- https://git.kernel.org/stable/c/f7989286175f32db8605e767a1a2efc62e894dc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72100.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

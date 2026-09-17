# [C] libceph: make decode_pool() more resilient against corrupted osdmaps

## Summary
Severity: Critical
Advisory: CVE-2025-71116
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71116
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: make decode_pool() more resilient against corrupted osdmaps

If the osdmap is (maliciously) corrupted such that the encoded length
of ceph_pg_pool envelope is less than what is expected for a particular
encoding version, out-of-bounds reads may ensue because the only bounds
check that is there is based on that length value.

This patch adds explicit bounds checks for each field that is decoded
or skipped.

## References
- https://git.kernel.org/stable/c/145d140abda80e33331c5781d6603014fa75d258
- https://git.kernel.org/stable/c/2acb8517429ab42146c6c0ac1daed1f03d2fd125
- https://git.kernel.org/stable/c/5d0d8c292531fe356c4e94dcfdf7d7212aca9957
- https://git.kernel.org/stable/c/8c738512714e8c0aa18f8a10c072d5b01c83db39
- https://git.kernel.org/stable/c/c82e39ff67353a5a6cbc07b786b8690bd2c45aaa
- https://git.kernel.org/stable/c/d061be4c8040ffb1110d537654a038b8b6ad39d2
- https://git.kernel.org/stable/c/e927ab132b87ba3f076705fc2684d94b24201ed1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71116.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

# [H] dm-flakey: Fix memory corruption in optional corrupt_bio_byte feature

## Summary
Severity: High
Advisory: CVE-2025-21966
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21966
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm-flakey: Fix memory corruption in optional corrupt_bio_byte feature

Fix memory corruption due to incorrect parameter being passed to bio_init

## References
- https://git.kernel.org/stable/c/57e9417f69839cb10f7ffca684c38acd28ceb57b
- https://git.kernel.org/stable/c/5a87e46da2418c57b445371f5ca0958d5779ba5f
- https://git.kernel.org/stable/c/818330f756f3800c37d738bd36bce60eac949938
- https://git.kernel.org/stable/c/da070843e153471be4297a12fdaa64023276f40e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21966.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21966
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

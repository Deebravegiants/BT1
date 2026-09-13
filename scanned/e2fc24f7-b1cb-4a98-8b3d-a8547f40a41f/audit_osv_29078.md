# [H] drm/amdgpu: add error handle to avoid out-of-bounds

## Summary
Severity: High
Advisory: CVE-2024-39471
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39471
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: add error handle to avoid out-of-bounds

if the sdma_v4_0_irq_id_to_seq return -EINVAL, the process should
be stop to avoid out-of-bounds read, so directly return -EINVAL.

## References
- https://git.kernel.org/stable/c/011552f29f20842c9a7a21bffe1f6a2d6457ba46
- https://git.kernel.org/stable/c/0964c84b93db7fbf74f357c1e20957850e092db3
- https://git.kernel.org/stable/c/5594971e02764aa1c8210ffb838cb4e7897716e8
- https://git.kernel.org/stable/c/5b0a3dc3e87821acb80e841b464d335aff242691
- https://git.kernel.org/stable/c/8112fa72b7f139052843ff484130d6f97e9f052f
- https://git.kernel.org/stable/c/8b2faf1a4f3b6c748c0da36cda865a226534d520
- https://git.kernel.org/stable/c/ea906e9ac61e3152bef63597f2d9f4a812fc346a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39471.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

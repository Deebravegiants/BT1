# [H] drm/amdgpu: validate the parameters of bo mapping operations more clearly

## Summary
Severity: High
Advisory: CVE-2024-26922
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-23
Source: https://osv.dev/vulnerability/CVE-2024-26922
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.157, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: validate the parameters of bo mapping operations more clearly

Verify the parameters of
amdgpu_vm_bo_(map/replace_map/clearing_mappings) in one common place.

## References
- https://git.kernel.org/stable/c/1fd7db5c16028dc07b2ceec190f2e895dddb532d
- https://git.kernel.org/stable/c/212e3baccdb1939606420d88f7f52d346b49a284
- https://git.kernel.org/stable/c/6fef2d4c00b5b8561ad68dd2b68173f5c6af1e75
- https://git.kernel.org/stable/c/8b12fc7b032633539acdf7864888b0ebd49e90f2
- https://git.kernel.org/stable/c/b1f04b9b1c5317f562a455384c5f7473e46bdbaa
- https://git.kernel.org/stable/c/d4da6b084f1c5625937d49bb6722c5b4aef11b8d
- https://git.kernel.org/stable/c/ef13eeca7c79136bc38e21eb67322c1cbd5c40ee
- https://git.kernel.org/stable/c/f68039375d4d6d67303674c0ab2d06b7295c0ec9
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26922.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

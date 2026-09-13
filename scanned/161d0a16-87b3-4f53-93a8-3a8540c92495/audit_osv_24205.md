# [M] scsi: fcoe: Fix transport not deattached when fcoe_if_init() fails

## Summary
Severity: Medium
Advisory: CVE-2022-50414
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50414
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: fcoe: Fix transport not deattached when fcoe_if_init() fails

fcoe_init() calls fcoe_transport_attach(&fcoe_sw_transport), but when
fcoe_if_init() fails, &fcoe_sw_transport is not detached and leaves freed
&fcoe_sw_transport on fcoe_transports list. This causes panic when
reinserting module.

 BUG: unable to handle page fault for address: fffffbfff82e2213
 RIP: 0010:fcoe_transport_attach+0xe1/0x230 [libfcoe]
 Call Trace:
  <TASK>
  do_one_initcall+0xd0/0x4e0
  load_module+0x5eee/0x7210
  ...

## References
- https://git.kernel.org/stable/c/09a60f908d8b6497f618113b7c3c31267dc90911
- https://git.kernel.org/stable/c/1dc499c615aa87dc46a3f2d1f91d2d358e55f3e3
- https://git.kernel.org/stable/c/22e8c7a56bb1cd2ed0beaaccb34282ac9cbbe27e
- https://git.kernel.org/stable/c/4155658cee394b22b24c6d64e49247bf26d95b92
- https://git.kernel.org/stable/c/aef82d16be5a353d913163f26fc4385e296be2b8
- https://git.kernel.org/stable/c/b5cc59470df64f26ad397dbb71cbf130cf489edf
- https://git.kernel.org/stable/c/be5f1a82ad6056db22c86005dc4cac22a20deeef
- https://git.kernel.org/stable/c/cf74d1197c0e3d2f353faa333e9e2847c73713f1
- https://git.kernel.org/stable/c/d581303d6f8d4139513105d73dd65f26c6707160
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50414.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

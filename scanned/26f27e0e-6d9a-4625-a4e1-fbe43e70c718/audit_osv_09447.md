# [M] CVE-2016-9912

## Summary
Severity: Medium
Advisory: CVE-2016-9912
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9912
Type: osv

## Details
Quick Emulator (Qemu) built with the Virtio GPU Device emulator support is vulnerable to a memory leakage issue. It could occur while destroying gpu resource object in 'virtio_gpu_resource_destroy'. A guest user/process could use this flaw to leak host memory bytes, resulting in DoS for a host.

## References
- http://www.securityfocus.com/bid/94760
- https://security.gentoo.org/glsa/201701-49
- http://www.openwall.com/lists/oss-security/2016/12/08/6

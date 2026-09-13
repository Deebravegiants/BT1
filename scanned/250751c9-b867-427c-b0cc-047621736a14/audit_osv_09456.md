# [M] CVE-2016-9923

## Summary
Severity: Medium
Advisory: CVE-2016-9923
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9923
Type: osv

## Details
Quick Emulator (Qemu) built with the 'chardev' backend support is vulnerable to a use after free issue. It could occur while hotplug and unplugging the device in the guest. A guest user/process could use this flaw to crash a Qemu process on the host resulting in DoS.

## References
- http://www.securityfocus.com/bid/94827
- https://security.gentoo.org/glsa/201701-49
- http://www.openwall.com/lists/oss-security/2016/12/09/2

# [C] CVE-2018-20961

## Summary
Severity: Critical
Advisory: CVE-2018-20961
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-07
Source: https://osv.dev/vulnerability/CVE-2018-20961
Type: osv

## Details
In the Linux kernel before 4.16.4, a double free vulnerability in the f_midi_set_alt function of drivers/usb/gadget/function/f_midi.c in the f_midi driver may allow attackers to cause a denial of service or possibly have unspecified other impact.

## References
- https://support.f5.com/csp/article/K58502654?utm_source=f5support&amp%3Butm_medium=RSS
- http://packetstormsecurity.com/files/154228/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.4
- https://seclists.org/bugtraq/2019/Aug/48
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://support.f5.com/csp/article/K58502654
- https://usn.ubuntu.com/4145-1/
- https://github.com/torvalds/linux/commit/7fafcfdf6377b18b2a726ea554d6e593ba44349f
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7fafcfdf6377b18b2a726ea554d6e593ba44349f

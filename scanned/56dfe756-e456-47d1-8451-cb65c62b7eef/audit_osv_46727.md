# [M] CVE-2014-9895

## Summary
Severity: Medium
Advisory: CVE-2014-9895
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2014-9895
Type: osv

## Details
drivers/media/media-device.c in the Linux kernel before 3.11, as used in Android before 2016-08-05 on Nexus 5 and 7 (2013) devices, does not properly initialize certain data structures, which allows local users to obtain sensitive information via a crafted application, aka Android internal bug 28750150 and Qualcomm internal bug CR570757, a different vulnerability than CVE-2014-1739.

## References
- http://source.android.com/security/bulletin/2016-08-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c88e739b1fad662240e99ecbd0bdaac871717987
- https://github.com/torvalds/linux/commit/c88e739b1fad662240e99ecbd0bdaac871717987
- https://source.codeaurora.org/quic/la/kernel/msm/commit/?id=cc4b26575602e492efd986e9a6ffc4278cee53b5
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c88e739b1fad662240e99ecbd0bdaac871717987
- https://github.com/torvalds/linux/commit/c88e739b1fad662240e99ecbd0bdaac871717987
- https://source.codeaurora.org/quic/la/kernel/msm/commit/?id=cc4b26575602e492efd986e9a6ffc4278cee53b5
- http://www.securityfocus.com/bid/92222

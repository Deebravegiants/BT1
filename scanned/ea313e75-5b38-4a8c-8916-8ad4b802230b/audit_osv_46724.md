# [H] CVE-2014-9870

## Summary
Severity: High
Advisory: CVE-2014-9870
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2014-9870
Type: osv

## Details
The Linux kernel before 3.11 on ARM platforms, as used in Android before 2016-08-05 on Nexus 5 and 7 (2013) devices, does not properly consider user-space access to the TPIDRURW register, which allows local users to gain privileges via a crafted application, aka Android internal bug 28749743 and Qualcomm internal bug CR561044.

## References
- http://source.android.com/security/bulletin/2016-08-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a4780adeefd042482f624f5e0d577bf9cdcbb760
- https://github.com/torvalds/linux/commit/a4780adeefd042482f624f5e0d577bf9cdcbb760
- https://source.codeaurora.org/quic/la/kernel/msm/commit/?id=4f57652fcd2dce7741f1ac6dc0417e2f265cd1de
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a4780adeefd042482f624f5e0d577bf9cdcbb760
- https://github.com/torvalds/linux/commit/a4780adeefd042482f624f5e0d577bf9cdcbb760
- https://source.codeaurora.org/quic/la/kernel/msm/commit/?id=4f57652fcd2dce7741f1ac6dc0417e2f265cd1de
- http://www.securityfocus.com/bid/92219

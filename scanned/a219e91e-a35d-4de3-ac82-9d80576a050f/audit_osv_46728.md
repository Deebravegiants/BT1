# [M] CVE-2014-9900

## Summary
Severity: Medium
Advisory: CVE-2014-9900
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2014-9900
Type: osv

## Details
The ethtool_get_wol function in net/core/ethtool.c in the Linux kernel through 4.7, as used in Android before 2016-08-05 on Nexus 5 and 7 (2013) devices, does not initialize a certain data structure, which allows local users to obtain sensitive information via a crafted application, aka Android internal bug 28803952 and Qualcomm internal bug CR570754.

## References
- http://source.android.com/security/bulletin/2016-08-01.html
- https://source.codeaurora.org/quic/la/kernel/msm-3.10/commit/?id=63c317dbee97983004dffdd9f742a20d17150071
- https://source.codeaurora.org/quic/la/kernel/msm-3.10/commit/?id=63c317dbee97983004dffdd9f742a20d17150071
- http://www.securityfocus.com/bid/92222

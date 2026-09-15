# [M] CVE-2014-9892

## Summary
Severity: Medium
Advisory: CVE-2014-9892
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2014-9892
Type: osv

## Details
The snd_compr_tstamp function in sound/core/compress_offload.c in the Linux kernel through 4.7, as used in Android before 2016-08-05 on Nexus 5 and 7 (2013) devices, does not properly initialize a timestamp data structure, which allows attackers to obtain sensitive information via a crafted application, aka Android internal bug 28770164 and Qualcomm internal bug CR568717.

## References
- http://source.android.com/security/bulletin/2016-08-01.html
- https://source.codeaurora.org/quic/la/kernel/msm-3.10/commit/?id=591b1f455c32206704cbcf426bb30911c260c33e
- https://source.codeaurora.org/quic/la/kernel/msm-3.10/commit/?id=591b1f455c32206704cbcf426bb30911c260c33e
- http://www.securityfocus.com/bid/92222

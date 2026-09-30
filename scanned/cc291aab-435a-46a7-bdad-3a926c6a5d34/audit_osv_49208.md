# [H] CVE-2018-5848

## Summary
Severity: High
Advisory: CVE-2018-5848
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-5848
Type: osv

## Details
In the function wmi_set_ie(), the length validation code does not handle unsigned integer overflow properly. As a result, a large value of the 'ie_len' argument can cause a buffer overflow in all Android releases from CAF (Android for MSM, Firefox OS for MSM, QRD Android) using the Linux Kernel.

## References
- https://source.android.com/security/bulletin/pixel/2018-05-01
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://www.codeaurora.org/security-bulletin/2018/05/11/may-2018-code-aurora-security-bulletin-2

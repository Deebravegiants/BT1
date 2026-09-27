# [M] CVE-2020-0404

## Summary
Severity: Medium
Advisory: CVE-2020-0404
Aliases: A-111893654, ASB-A-111893654
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0404
Type: osv

## Details
In uvc_scan_chain_forward of uvc_driver.c, there is a possible linked list corruption due to an unusual root cause. This could lead to local escalation of privilege in the kernel with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-111893654References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2020-09-01
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html

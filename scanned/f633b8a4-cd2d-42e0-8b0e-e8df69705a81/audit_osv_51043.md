# [H] CVE-2021-0326

## Summary
Severity: High
Advisory: CVE-2021-0326
Aliases: A-172937525, ASB-A-172937525
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-10
Source: https://osv.dev/vulnerability/CVE-2021-0326
Type: osv

## Details
In p2p_copy_client_info of p2p.c, there is a possible out of bounds write due to a missing bounds check. This could lead to remote code execution if the target device is performing a Wi-Fi Direct search, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-10 Android-11 Android-8.1 Android-9Android ID: A-172937525

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VMHPFCON6ZFCGZXSASJFKQ3UX2UIYMND/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VOSA6DZUDLVOCYJNNXD6V3MRBVLCXZFH/
- https://www.debian.org/security/2021/dsa-4898
- https://lists.debian.org/debian-lts-announce/2021/02/msg00033.html
- https://source.android.com/security/bulletin/2021-02-01

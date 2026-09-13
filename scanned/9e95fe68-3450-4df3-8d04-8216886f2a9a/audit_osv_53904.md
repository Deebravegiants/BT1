# [H] CVE-2023-3217

## Summary
Severity: High
Advisory: CVE-2023-3217
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-13
Source: https://osv.dev/vulnerability/CVE-2023-3217
Type: osv

## Details
Use after free in WebXR in Google Chrome prior to 114.0.5735.133 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- http://packetstormsecurity.com/files/173495/Chrome-device-OpenXrApiWrapper-InitSession-Heap-Use-After-Free.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JEH75UOM7FAXDUPC37YHP7ONL2HSDIJR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O362DC3ZCFRXVHOXMPIL73YOWABQEUYD/
- https://security.gentoo.org/glsa/202311-11
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5428
- https://chromereleases.googleblog.com/2023/06/stable-channel-update-for-desktop_13.html
- https://crbug.com/1450601

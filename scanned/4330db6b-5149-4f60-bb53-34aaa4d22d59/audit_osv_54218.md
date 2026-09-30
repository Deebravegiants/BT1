# [H] CVE-2023-4354

## Summary
Severity: High
Advisory: CVE-2023-4354
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-15
Source: https://osv.dev/vulnerability/CVE-2023-4354
Type: osv

## Details
Heap buffer overflow in Skia in Google Chrome prior to 116.0.5845.96 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- http://packetstormsecurity.com/files/174949/Chrome-SKIA-Integer-Overflow.html
- https://chromereleases.googleblog.com/2023/08/stable-channel-update-for-desktop_15.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DMXHPRUGBUDNHZCZCIVMWAUIEXEGMGT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OCFEK63FUHFXZH5MSG6TNQOXMQWM4M5S/
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5479
- https://crbug.com/1464215

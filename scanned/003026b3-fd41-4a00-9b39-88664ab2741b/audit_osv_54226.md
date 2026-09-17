# [H] CVE-2023-4362

## Summary
Severity: High
Advisory: CVE-2023-4362
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-15
Source: https://osv.dev/vulnerability/CVE-2023-4362
Type: osv

## Details
Heap buffer overflow in Mojom IDL in Google Chrome prior to 116.0.5845.96 allowed a remote attacker who had compromised the renderer process and gained control of a WebUI process to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: Medium)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2DMXHPRUGBUDNHZCZCIVMWAUIEXEGMGT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OCFEK63FUHFXZH5MSG6TNQOXMQWM4M5S/
- https://security.gentoo.org/glsa/202401-34
- https://www.debian.org/security/2023/dsa-5479
- https://chromereleases.googleblog.com/2023/08/stable-channel-update-for-desktop_15.html
- https://crbug.com/1316379

# [H] JLSEC-2026-581

## Summary
Severity: High
Advisory: JLSEC-2026-581
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-581
Type: osv

## Affected
- Julia: `XSLT_jll` — affected >=0 <1.1.41+0

## Details
Use after free in Blink XSLT in Google Chrome prior to 91.0.4472.164 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

## References
- https://chromereleases.googleblog.com/2021/07/stable-channel-update-for-desktop.html
- https://crbug.com/1219209
- https://lists.debian.org/debian-lts-announce/2022/09/msg00010.html
- https://security.gentoo.org/glsa/202310-23
- https://www.debian.org/security/2022/dsa-5216

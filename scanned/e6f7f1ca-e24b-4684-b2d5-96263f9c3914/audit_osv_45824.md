# [H] JLSEC-2026-375

## Summary
Severity: High
Advisory: JLSEC-2026-375
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/JLSEC-2026-375
Type: osv

## Affected
- Julia: `LibVPX_jll` — affected >=0 <1.15.2+0

## Details
Heap buffer overflow in vp8 encoding in libvpx in Google Chrome prior to 117.0.5938.132 and libvpx 1.13.1 allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- http://seclists.org/fulldisclosure/2023/Oct/12
- http://seclists.org/fulldisclosure/2023/Oct/16
- http://www.openwall.com/lists/oss-security/2023/09/28/5
- http://www.openwall.com/lists/oss-security/2023/09/28/6
- http://www.openwall.com/lists/oss-security/2023/09/29/1
- http://www.openwall.com/lists/oss-security/2023/09/29/11
- http://www.openwall.com/lists/oss-security/2023/09/29/12
- http://www.openwall.com/lists/oss-security/2023/09/29/14
- http://www.openwall.com/lists/oss-security/2023/09/29/2
- http://www.openwall.com/lists/oss-security/2023/09/29/7
- http://www.openwall.com/lists/oss-security/2023/09/29/9
- http://www.openwall.com/lists/oss-security/2023/09/30/1
- http://www.openwall.com/lists/oss-security/2023/09/30/2
- http://www.openwall.com/lists/oss-security/2023/09/30/3
- http://www.openwall.com/lists/oss-security/2023/09/30/4
- http://www.openwall.com/lists/oss-security/2023/09/30/5
- http://www.openwall.com/lists/oss-security/2023/10/01/1
- http://www.openwall.com/lists/oss-security/2023/10/01/2
- http://www.openwall.com/lists/oss-security/2023/10/01/5
- http://www.openwall.com/lists/oss-security/2023/10/02/6

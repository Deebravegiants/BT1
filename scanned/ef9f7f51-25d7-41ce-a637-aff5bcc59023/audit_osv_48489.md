# [H] CVE-2017-8311

## Summary
Severity: High
Advisory: CVE-2017-8311
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-8311
Type: osv

## Details
Potential heap based buffer overflow in ParseJSS in VideoLAN VLC before 2.2.5 due to skipping NULL terminator in an input string allows attackers to execute arbitrary code via a crafted subtitles file.

## References
- https://www.exploit-db.com/exploits/44514/
- http://git.videolan.org/?p=vlc.git%3Ba=commitdiff%3Bh=775de716add17322f24b476439f903a829446eb6
- http://www.securityfocus.com/bid/98634
- https://security.gentoo.org/glsa/201707-10
- http://www.debian.org/security/2017/dsa-3899

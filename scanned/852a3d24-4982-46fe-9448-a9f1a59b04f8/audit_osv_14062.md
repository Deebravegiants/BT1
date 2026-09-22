# [M] CVE-2018-6849

## Summary
Severity: Medium
Advisory: CVE-2018-6849
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2018-04-01
Source: https://osv.dev/vulnerability/CVE-2018-6849
Type: osv

## Details
In the WebRTC component in DuckDuckGo 4.2.0, after visiting a web site that attempts to gather complete client information (such as https://ip.voidsec.com), the browser can disclose a private IP address in a STUN request.

## References
- https://datarift.blogspot.com/p/private-ip-leakage-using-webrtc.html
- https://news.ycombinator.com/item?id=16699270
- https://voidsec.com/vpn-leak/
- https://github.com/rapid7/metasploit-framework/pull/9538
- https://www.exploit-db.com/exploits/44403/

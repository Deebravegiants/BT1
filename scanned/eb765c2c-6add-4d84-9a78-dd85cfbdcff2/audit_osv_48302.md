# [H] CVE-2017-5982

## Summary
Severity: High
Advisory: CVE-2017-5982
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-28
Source: https://osv.dev/vulnerability/CVE-2017-5982
Type: osv

## Details
Directory traversal vulnerability in the Chorus2 2.4.2 add-on for Kodi allows remote attackers to read arbitrary files via a %2E%2E%252e (encoded dot dot slash) in the image path, as demonstrated by image/image%3A%2F%2F%2e%2e%252fetc%252fpasswd.

## References
- http://www.securityfocus.com/bid/96481
- https://lists.debian.org/debian-lts-announce/2024/01/msg00009.html
- http://packetstormsecurity.com/files/141043/Kodi-17.1-Arbitrary-File-Disclosure.html
- http://seclists.org/fulldisclosure/2017/Feb/27
- https://www.exploit-db.com/exploits/41312/

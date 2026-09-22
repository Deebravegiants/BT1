# [H] JLSEC-2026-398

## Summary
Severity: High
Advisory: JLSEC-2026-398
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-398
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=7.81.0+0 <7.87.0+0

## Details
curl before 7.86.0 has a double free. If curl is told to use an HTTP proxy for a transfer with a non-HTTP(S) URL, it sets up the connection to the remote server by issuing a CONNECT request to the proxy, and then tunnels the rest of the protocol through. An HTTP proxy might refuse this request (HTTP proxies often only allow outgoing connections to specific port numbers, like 443 for HTTPS) and instead return a non-200 status code to the client. Due to flaws in the error/cleanup handling, this could trigger a double free in curl if one of the following schemes were used in the URL for the transfer: dict, gopher, gophers, ldap, ldaps, rtmp, rtmps, or telnet. The earliest affected version is 7.77.0.

## References
- http://seclists.org/fulldisclosure/2023/Jan/19
- http://seclists.org/fulldisclosure/2023/Jan/20
- https://curl.se/docs/CVE-2022-42915.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/37YEVVC6NAF6H7UHH6YAUY5QEVY6LIH2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HVU3IMZCKR4VE6KJ4GCWRL2ILLC6OV76/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q27V5YYMXUVI6PRZQVECON32XPVWTKDK/
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20221209-0010/
- https://support.apple.com/kb/HT213604
- https://support.apple.com/kb/HT213605

# [C] JLSEC-2026-396

## Summary
Severity: Critical
Advisory: JLSEC-2026-396
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-396
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <7.87.0+0

## Details
When doing HTTP(S) transfers, libcurl might erroneously use the read callback (`CURLOPT_READFUNCTION`) to ask for data to send, even when the `CURLOPT_POSTFIELDS` option has been set, if the same handle previously was used to issue a `PUT` request which used that callback. This flaw may surprise the application and cause it to misbehave and either send off the wrong data or use memory after free or similar in the subsequent `POST` request. The problem exists in the logic for a reused handle when it is changed from a PUT to a POST.

## References
- http://seclists.org/fulldisclosure/2023/Jan/19
- http://seclists.org/fulldisclosure/2023/Jan/20
- http://www.openwall.com/lists/oss-security/2023/05/17/4
- https://hackerone.com/reports/1704017
- https://lists.debian.org/debian-lts-announce/2023/01/msg00028.html
- https://security.gentoo.org/glsa/202212-01
- https://security.netapp.com/advisory/ntap-20230110-0006/
- https://security.netapp.com/advisory/ntap-20230208-0002/
- https://support.apple.com/kb/HT213604
- https://support.apple.com/kb/HT213605
- https://www.debian.org/security/2023/dsa-5330

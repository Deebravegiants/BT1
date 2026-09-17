# [M] JLSEC-2026-409

## Summary
Severity: Medium
Advisory: JLSEC-2026-409
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-409
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.2.1+0

## Details
An improper certificate validation vulnerability exists in curl <v8.1.0 in the way it supports matching of wildcard patterns when listed as "Subject Alternative Name" in TLS server certificates. curl can be built to use its own name matching function for TLS rather than one provided by a TLS library. This private wildcard matching function would match IDN (International Domain Name) hosts incorrectly and could as a result accept patterns that otherwise should mismatch. IDN hostnames are converted to puny code before used for certificate checks. Puny coded names always start with `xn--` and should not be allowed to pattern match, but the wildcard check in curl could still check for `x*`, which would match even though the IDN name most likely contained nothing even resembling an `x`.

## References
- http://seclists.org/fulldisclosure/2023/Jul/47
- http://seclists.org/fulldisclosure/2023/Jul/48
- http://seclists.org/fulldisclosure/2023/Jul/52
- https://hackerone.com/reports/1950627
- https://lists.debian.org/debian-lts-announce/2023/10/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F4I75RDGX5ULSSCBE5BF3P5I5SFO7ULQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z2LIWHWKOVH24COGGBCVOWDXXIUPKOMK/
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230609-0009/
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845

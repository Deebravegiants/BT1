# [M] CVE-2023-28321

## Summary
Severity: Medium
Advisory: CVE-2023-28321
Aliases: CURL-CVE-2023-28321
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-28321
Type: osv

## Details
An improper certificate validation vulnerability exists in curl <v8.1.0 in the way it supports matching of wildcard patterns when listed as "Subject Alternative Name" in TLS server certificates. curl can be built to use its own name matching function for TLS rather than one provided by a TLS library. This private wildcard matching function would match IDN (International Domain Name) hosts incorrectly and could as a result accept patterns that otherwise should mismatch. IDN hostnames are converted to puny code before used for certificate checks. Puny coded names always start with `xn--` and should not be allowed to pattern match, but the wildcard check in curl could still check for `x*`, which would match even though the IDN name most likely contained nothing even resembling an `x`.

## References
- https://hackerone.com/reports/1950627
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28321.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F4I75RDGX5ULSSCBE5BF3P5I5SFO7ULQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z2LIWHWKOVH24COGGBCVOWDXXIUPKOMK/
- https://nvd.nist.gov/vuln/detail/CVE-2023-28321
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230609-0009/
- http://seclists.org/fulldisclosure/2023/Jul/47
- http://seclists.org/fulldisclosure/2023/Jul/48
- http://seclists.org/fulldisclosure/2023/Jul/52
- https://lists.debian.org/debian-lts-announce/2023/10/msg00016.html

# [H] CVE-2020-15049

## Summary
Severity: High
Advisory: CVE-2020-15049
Aliases: GHSA-qf3v-rc95-96j5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-15049
Type: osv

## Details
An issue was discovered in http/ContentLengthInterpreter.cc in Squid before 4.12 and 5.x before 5.0.3. A Request Smuggling and Poisoning attack can succeed against the HTTP cache. The client sends an HTTP request with a Content-Length header containing "+\ "-" or an uncommon shell whitespace character prefix to the length field-value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3RG5FGSTCAYVIJPJHIY3MRZ7NFT6HDO7/
- https://usn.ubuntu.com/4551-1/
- https://github.com/squid-cache/squid/security/advisories/GHSA-qf3v-rc95-96j5
- https://security.netapp.com/advisory/ntap-20210312-0001/
- https://www.debian.org/security/2020/dsa-4732
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-ea12a34d338b962707d5078d6d1fc7c6eb119a22.patch
- http://www.squid-cache.org/Versions/v5/changesets/squid-5-485c9a7bb1bba88754e07ad0094647ea57a6eb8d.patch

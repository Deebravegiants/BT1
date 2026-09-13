# [M] CVE-2023-28322

## Summary
Severity: Medium
Advisory: CVE-2023-28322
Aliases: CURL-CVE-2023-28322
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-28322
Type: osv

## Details
An information disclosure vulnerability exists in curl <v8.1.0 when doing HTTP(S) transfers, libcurl might erroneously use the read callback (`CURLOPT_READFUNCTION`) to ask for data to send, even when the `CURLOPT_POSTFIELDS` option has been set, if the same handle previously wasused to issue a `PUT` request which used that callback. This flaw may surprise the application and cause it to misbehave and either send off the wrong data or use memory after free or similar in the second transfer. The problem exists in the logic for a reused handle when it is (expected to be) changed from a PUT to a POST.

## References
- https://hackerone.com/reports/1954658
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28322.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F4I75RDGX5ULSSCBE5BF3P5I5SFO7ULQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z2LIWHWKOVH24COGGBCVOWDXXIUPKOMK/
- https://nvd.nist.gov/vuln/detail/CVE-2023-28322
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230609-0009/
- http://seclists.org/fulldisclosure/2023/Jul/47
- http://seclists.org/fulldisclosure/2023/Jul/48
- http://seclists.org/fulldisclosure/2023/Jul/52
- https://lists.debian.org/debian-lts-announce/2023/12/msg00015.html

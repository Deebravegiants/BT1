# [C] CVE-2021-3466

## Summary
Severity: Critical
Advisory: CVE-2021-3466
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/CVE-2021-3466
Type: osv

## Details
A flaw was found in libmicrohttpd. A missing bounds check in the post_process_urlencoded function leads to a buffer overflow, allowing a remote attacker to write arbitrary data in an application that uses libmicrohttpd. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability. Only version 0.9.70 is vulnerable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4334XJNDJPYQNFE6S3S2KUJJ7TMHYCWL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/75HDMREKITMGPGE62NP7KE62ZJVLETXN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K5NEPVGP3L2CZHLZ4UB44PEILHKPDBOG/
- https://security.gentoo.org/glsa/202311-08
- https://bugzilla.redhat.com/show_bug.cgi?id=1939127

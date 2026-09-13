# [H] CVE-2016-6328

## Summary
Severity: High
Advisory: CVE-2016-6328
Aliases: A-162602132, ASB-A-162602132
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2016-6328
Type: osv

## Details
A vulnerability was found in libexif. An integer overflow when parsing the MNOTE entry data of the input file. This can cause Denial-of-Service (DoS) and Information Disclosure (disclosing some critical heap chunk metadata, even other applications' private data).

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00016.html
- https://security.gentoo.org/glsa/202007-05
- https://usn.ubuntu.com/4277-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-6328

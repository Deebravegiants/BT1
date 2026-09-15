# [H] CVE-2017-11108

## Summary
Severity: High
Advisory: CVE-2017-11108
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-08
Source: https://osv.dev/vulnerability/CVE-2017-11108
Type: osv

## Details
tcpdump 4.9.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via crafted packet data. The crash occurs in the EXTRACT_16BITS function, called from the stp_print function for the Spanning Tree Protocol.

## References
- https://support.apple.com/HT208221
- http://www.debian.org/security/2017/dsa-3971
- https://access.redhat.com/errata/RHEA-2018:0705
- https://security.gentoo.org/glsa/201709-23
- https://bugzilla.redhat.com/show_bug.cgi?id=1468504

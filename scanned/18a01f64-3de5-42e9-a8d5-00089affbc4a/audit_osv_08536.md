# [H] CVE-2016-4301

## Summary
Severity: High
Advisory: CVE-2016-4301
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-4301
Type: osv

## Details
Stack-based buffer overflow in the parse_device function in archive_read_support_format_mtree.c in libarchive before 3.2.1 allows remote attackers to execute arbitrary code via a crafted mtree file.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91328
- https://security.gentoo.org/glsa/201701-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1348441
- https://github.com/libarchive/libarchive/commit/a550daeecf6bc689ade371349892ea17b5b97c77
- https://github.com/libarchive/libarchive/issues/715
- http://blog.talosintel.com/2016/06/the-poisoned-archives.html
- http://www.talosintel.com/reports/TALOS-2016-0153/

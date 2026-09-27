# [H] CVE-2016-4302

## Summary
Severity: High
Advisory: CVE-2016-4302
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-4302
Type: osv

## Details
Heap-based buffer overflow in the parse_codes function in archive_read_support_format_rar.c in libarchive before 3.2.1 allows remote attackers to execute arbitrary code via a RAR file with a zero-sized dictionary.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.securityfocus.com/bid/91331
- https://security.gentoo.org/glsa/201701-03
- http://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=1348444
- https://github.com/libarchive/libarchive/commit/05caadc7eedbef471ac9610809ba683f0c698700
- https://github.com/libarchive/libarchive/issues/719
- http://blog.talosintel.com/2016/06/the-poisoned-archives.html
- http://www.talosintel.com/reports/TALOS-2016-0154/

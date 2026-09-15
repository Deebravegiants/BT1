# [H] CVE-2016-4300

## Summary
Severity: High
Advisory: CVE-2016-4300
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/CVE-2016-4300
Type: osv

## Details
Integer overflow in the read_SubStreamsInfo function in archive_read_support_format_7zip.c in libarchive before 3.2.1 allows remote attackers to execute arbitrary code via a 7zip file with a large number of substreams, which triggers a heap-based buffer overflow.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://rhn.redhat.com/errata/RHSA-2016-1844.html
- http://www.debian.org/security/2016/dsa-3657
- http://www.securityfocus.com/bid/91326
- https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00062&languageid=en-fr
- https://security.gentoo.org/glsa/201701-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1348439
- https://github.com/libarchive/libarchive/commit/e79ef306afe332faf22e9b442a2c6b59cb175573
- https://github.com/libarchive/libarchive/issues/718
- http://blog.talosintel.com/2016/06/the-poisoned-archives.html
- http://www.talosintel.com/reports/TALOS-2016-0152/

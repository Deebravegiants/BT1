# [H] CVE-2015-7747

## Summary
Severity: High
Advisory: CVE-2015-7747
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-19
Source: https://osv.dev/vulnerability/CVE-2015-7747
Type: osv

## Details
Buffer overflow in the afReadFrames function in audiofile (aka libaudiofile and Audio File Library) allows user-assisted remote attackers to cause a denial of service (program crash) or possibly execute arbitrary code via a crafted audio file, as demonstrated by sixteen-stereo-to-eight-mono.c.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/170387.html
- http://www.openwall.com/lists/oss-security/2015/10/06/2
- http://www.ubuntu.com/usn/USN-2787-1
- https://bugs.launchpad.net/ubuntu/+source/audiofile/+bug/1502721
- https://github.com/ccrisan/motioneyeos/blob/master/package/audiofile/0008-CVE-2015-7747.patch
- https://www.openwall.com/lists/oss-security/2015/10/08/1
- http://www.openwall.com/lists/oss-security/2015/10/06/2
- https://www.openwall.com/lists/oss-security/2015/10/08/1
- https://github.com/ccrisan/motioneyeos/blob/master/package/audiofile/0008-CVE-2015-7747.patch

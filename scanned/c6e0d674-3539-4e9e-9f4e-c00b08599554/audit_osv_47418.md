# [H] CVE-2016-4973

## Summary
Severity: High
Advisory: CVE-2016-4973
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-07
Source: https://osv.dev/vulnerability/CVE-2016-4973
Type: osv

## Details
Binaries compiled against targets that use the libssp library in GCC for stack smashing protection (SSP) might allow local users to perform buffer overflow attacks by leveraging lack of the Object Size Checking feature.

## References
- http://www.openwall.com/lists/oss-security/2016/08/17/6
- http://www.securityfocus.com/bid/92530
- https://bugzilla.redhat.com/show_bug.cgi?id=1324759
- http://www.openwall.com/lists/oss-security/2016/08/17/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1324759

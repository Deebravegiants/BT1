# [H] CVE-2016-4794

## Summary
Severity: High
Advisory: CVE-2016-4794
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4794
Type: osv

## Details
Use-after-free vulnerability in mm/percpu.c in the Linux kernel through 4.6 allows local users to cause a denial of service (BUG) or possibly have unspecified other impact via crafted use of the mmap and bpf system calls.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.ubuntu.com/usn/USN-3054-1
- http://www.ubuntu.com/usn/USN-3055-1
- https://source.android.com/security/bulletin/2016-12-01.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.securityfocus.com/bid/90625
- http://www.ubuntu.com/usn/USN-3053-1
- http://www.ubuntu.com/usn/USN-3056-1
- http://www.ubuntu.com/usn/USN-3057-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1335889
- http://www.openwall.com/lists/oss-security/2016/05/12/6
- https://lkml.org/lkml/2016/4/17/125

# [M] CVE-2016-9011

## Summary
Severity: Medium
Advisory: CVE-2016-9011
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9011
Type: osv

## Details
The wmf_malloc function in api.c in libwmf 0.2.8.4 allows remote attackers to cause a denial of service (application crash) via a crafted wmf file, which triggers a memory allocation failure.

## References
- http://www.openwall.com/lists/oss-security/2016/10/25/1
- http://www.securityfocus.com/bid/93860
- https://blogs.gentoo.org/ago/2016/10/18/libwmf-memory-allocation-failure-in-wmf_malloc-api-c
- https://bugzilla.redhat.com/show_bug.cgi?id=1388450

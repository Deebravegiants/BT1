# [H] CVE-2017-9951

## Summary
Severity: High
Advisory: CVE-2017-9951
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-9951
Type: osv

## Details
The try_read_command function in memcached.c in memcached before 1.4.39 allows remote attackers to cause a denial of service (segmentation fault) via a request to add/set a key, which makes a comparison between signed and unsigned int and triggers a heap-based buffer over-read. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-8705.

## References
- http://www.securityfocus.com/bid/99874
- https://usn.ubuntu.com/3588-1/
- https://github.com/memcached/memcached/wiki/ReleaseNotes1439
- https://groups.google.com/forum/message/raw?msg=memcached/ubGWrkmrr4E/nrm1SeVJAQAJ
- https://www.debian.org/security/2018/dsa-4218
- https://www.twistlock.com/2017/07/13/cve-2017-9951-heap-overflow-memcached-server-1-4-38-twistlock-vulnerability-report/

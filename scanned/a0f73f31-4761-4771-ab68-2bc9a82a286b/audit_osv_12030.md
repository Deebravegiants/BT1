# [C] CVE-2018-1000802

## Summary
Severity: Critical
Advisory: CVE-2018-1000802
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-18
Source: https://osv.dev/vulnerability/CVE-2018-1000802
Type: osv

## Details
Python Software Foundation Python (CPython) version 2.7 contains a CWE-77: Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in shutil module (make_archive function) that can result in Denial of service, Information gain via injection of arbitrary files on the system or entire drive. This attack appear to be exploitable via Passage of unfiltered user input to the function. This vulnerability appears to have been fixed in after commit add531a1e55b0a739b0f42582f1c9747e5649ace.

## References
- https://mega.nz/#%21JUFiCC4R%21mq-jQ8ySFwIhX6WMDujaZuNBfttDVt7DETlfOIQE1ig
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00031.html
- https://security.netapp.com/advisory/ntap-20230309-0002/
- https://usn.ubuntu.com/3817-1/
- https://usn.ubuntu.com/3817-2/
- https://www.debian.org/security/2018/dsa-4306
- https://bugs.python.org/issue34540
- https://github.com/python/cpython/pull/8985
- https://github.com/python/cpython/pull/8985/commits/add531a1e55b0a739b0f42582f1c9747e5649ace

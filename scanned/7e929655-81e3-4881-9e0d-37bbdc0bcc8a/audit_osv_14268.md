# [M] CVE-2018-8754

## Summary
Severity: Medium
Advisory: CVE-2018-8754
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-18
Source: https://osv.dev/vulnerability/CVE-2018-8754
Type: osv

## Details
The libevt_record_values_read_event() function in libevt_record_values.c in libevt before 2018-03-17 does not properly check for out-of-bounds values of user SID data size, strings size, or data size. NOTE: the vendor has disputed this as described in libyal/libevt issue 5 on GitHub

## References
- https://www.debian.org/security/2018/dsa-4160
- https://github.com/libyal/libevt/commit/9d2cc3ca0a1612a6b271abcacffc2e3eea42925e

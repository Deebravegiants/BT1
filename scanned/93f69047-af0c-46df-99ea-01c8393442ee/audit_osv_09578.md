# [H] CVE-2017-1000199

## Summary
Severity: High
Advisory: CVE-2017-1000199
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-1000199
Type: osv

## Details
tcmu-runner version 0.91 up to 1.20 is vulnerable to information disclosure in handler_qcow.so resulting in non-privileged users being able to check for existence of any file with root privileges.

## References
- https://access.redhat.com/errata/RHSA-2017:3277
- https://github.com/open-iscsi/tcmu-runner/issues/194

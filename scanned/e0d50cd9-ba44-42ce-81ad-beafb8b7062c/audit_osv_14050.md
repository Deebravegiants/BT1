# [H] CVE-2018-6611

## Summary
Severity: High
Advisory: CVE-2018-6611
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-04
Source: https://osv.dev/vulnerability/CVE-2018-6611
Type: osv

## Details
soundlib/Load_stp.cpp in OpenMPT through 1.27.04.00, and libopenmpt before 0.3.6, has an out-of-bounds read via a malformed STP file.

## References
- https://github.com/OpenMPT/openmpt/commit/b60b322cf9f0ffa624018f1bb9783edf0dc908c3
- https://lib.openmpt.org/libopenmpt/2018/02/03/security-update-0.3.6/

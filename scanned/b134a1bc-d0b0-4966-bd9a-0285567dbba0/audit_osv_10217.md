# [H] CVE-2017-14339

## Summary
Severity: High
Advisory: CVE-2017-14339
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2017-14339
Type: osv

## Details
The DNS packet parser in YADIFA before 2.2.6 does not check for the presence of infinite pointer loops, and thus it is possible to force it to enter an infinite loop. This can cause high CPU usage and makes the server unresponsive.

## References
- http://www.debian.org/security/2017/dsa-4001
- https://github.com/yadifa/yadifa/blob/v2.2.6/ChangeLog
- https://www.tarlogic.com/blog/fuzzing-yadifa-dns/

# [H] CVE-2018-13420

## Summary
Severity: High
Advisory: CVE-2018-13420
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-07
Source: https://osv.dev/vulnerability/CVE-2018-13420
Type: osv

## Details
Google gperftools 2.7 has a memory leak in malloc_extension.cc, related to MallocExtension::Register and InitModule. NOTE: the software maintainer indicates that this is not a bug; it is only a false-positive report from the LeakSanitizer program

## References
- https://github.com/gperftools/gperftools/issues/1013

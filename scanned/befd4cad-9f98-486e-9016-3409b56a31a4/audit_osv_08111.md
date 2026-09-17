# [H] CVE-2016-10320

## Summary
Severity: High
Advisory: CVE-2016-10320
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-06
Source: https://osv.dev/vulnerability/CVE-2016-10320
Type: osv

## Details
textract before 1.5.0 allows OS Command Injection attacks via a filename in a call to the process function. This may be a remote attack if a web application accepts names of arbitrary uploaded files.

## References
- http://seclists.org/oss-sec/2016/q4/442

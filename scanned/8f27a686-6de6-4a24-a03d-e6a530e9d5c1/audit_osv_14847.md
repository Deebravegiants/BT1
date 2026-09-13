# [C] CVE-2019-11888

## Summary
Severity: Critical
Advisory: CVE-2019-11888
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/CVE-2019-11888
Type: osv

## Details
Go through 1.12.5 on Windows mishandles process creation with a nil environment in conjunction with a non-nil token, which allows attackers to obtain sensitive information or gain privileges.

## References
- https://go-review.googlesource.com/c/go/+/176619

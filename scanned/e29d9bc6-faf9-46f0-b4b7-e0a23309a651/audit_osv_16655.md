# [M] CVE-2019-8790

## Summary
Severity: Medium
Advisory: CVE-2019-8790
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-27
Source: https://osv.dev/vulnerability/CVE-2019-8790
Type: osv

## Details
This issue was addresses by updating incorrect URLSession file descriptors management logic to match Swift 5.0. This issue is fixed in Swift 5.1.1 for Ubuntu. Incorrect management of file descriptors in URLSession could lead to inadvertent data disclosure.

## References
- https://support.apple.com/en-us/HT210647

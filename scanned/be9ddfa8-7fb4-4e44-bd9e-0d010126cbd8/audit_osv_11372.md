# [H] CVE-2017-7570

## Summary
Severity: High
Advisory: CVE-2017-7570
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-07
Source: https://osv.dev/vulnerability/CVE-2017-7570
Type: osv

## Details
PivotX 2.3.11 allows remote authenticated Advanced users to execute arbitrary PHP code by performing an upload with a safe file extension (such as .jpg) and then invoking the duplicate function to change to the .php extension.

## References
- https://gist.github.com/X1nda/749b6aac6e080624d9f8ec81321335df

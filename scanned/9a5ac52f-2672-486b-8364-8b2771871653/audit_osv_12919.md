# [C] CVE-2018-16367

## Summary
Severity: Critical
Advisory: CVE-2018-16367
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-09-02
Source: https://osv.dev/vulnerability/CVE-2018-16367
Type: osv

## Details
In OnlineJudge 2.0, the sandbox has an incorrect access control vulnerability that can write a file anywhere. A user can write a directory listing to /tmp, and can leak file data with a #include.

## References
- https://github.com/QingdaoU/OnlineJudge/issues/165

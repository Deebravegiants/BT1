# [H] CVE-2019-10245

## Summary
Severity: High
Advisory: CVE-2019-10245
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-19
Source: https://osv.dev/vulnerability/CVE-2019-10245
Type: osv

## Details
In Eclipse OpenJ9 prior to the 0.14.0 release, the Java bytecode verifier incorrectly allows a method to execute past the end of bytecode array causing crashes. Eclipse OpenJ9 v0.14.0 correctly detects this case and rejects the attempted class load.

## References
- http://www.securityfocus.com/bid/108094
- https://access.redhat.com/errata/RHSA-2019:1163
- https://access.redhat.com/errata/RHSA-2019:1164
- https://access.redhat.com/errata/RHSA-2019:1165
- https://access.redhat.com/errata/RHSA-2019:1166
- https://access.redhat.com/errata/RHSA-2019:1238
- https://access.redhat.com/errata/RHSA-2019:1325
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=545588

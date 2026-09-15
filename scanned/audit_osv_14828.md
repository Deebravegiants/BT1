# [H] CVE-2019-11775

## Summary
Severity: High
Advisory: CVE-2019-11775
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-11775
Type: osv

## Details
All builds of Eclipse OpenJ9 prior to 0.15 contain a bug where the loop versioner may fail to privatize a value that is pulled out of the loop by versioning - for example if there is a condition that is moved out of the loop that reads a field we may not privatize the value of that field in the modified copy of the loop allowing the test to see one value of the field and subsequently the loop to see a modified field value without retesting the condition moved out of the loop. This can lead to a variety of different issues but read out of array bounds is one major consequence of these problems.

## References
- https://access.redhat.com/errata/RHSA-2019:2494
- https://access.redhat.com/errata/RHSA-2019:2495
- https://access.redhat.com/errata/RHSA-2019:2585
- https://access.redhat.com/errata/RHSA-2019:2590
- https://access.redhat.com/errata/RHSA-2019:2592
- https://access.redhat.com/errata/RHSA-2019:2737
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=549601

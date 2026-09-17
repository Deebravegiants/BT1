# [C] CVE-2020-27221

## Summary
Severity: Critical
Advisory: CVE-2020-27221
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-21
Source: https://osv.dev/vulnerability/CVE-2020-27221
Type: osv

## Details
In Eclipse OpenJ9 up to and including version 0.23, there is potential for a stack-based buffer overflow when the virtual machine or JNI natives are converting from UTF-8 characters to platform encoding.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=569763

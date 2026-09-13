# [H] CVE-2021-41034

## Summary
Severity: High
Advisory: CVE-2021-41034
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-29
Source: https://osv.dev/vulnerability/CVE-2021-41034
Type: osv

## Details
The build of some language stacks of Eclipse Che version 6 includes pulling some binaries from an unsecured HTTP endpoint. As a consequence the builds of such stacks are vulnerable to MITM attacks that allow the replacement of the original binaries with arbitrary ones. The stacks involved are Java 8 (alpine and centos), Android and PHP. The vulnerability is not exploitable at runtime but only when building Che.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=540989

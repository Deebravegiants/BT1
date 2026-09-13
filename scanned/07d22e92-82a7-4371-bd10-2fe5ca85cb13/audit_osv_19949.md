# [M] CVE-2021-28167

## Summary
Severity: Medium
Advisory: CVE-2021-28167
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2021-28167
Type: osv

## Details
In Eclipse Openj9 to version 0.25.0, usage of the jdk.internal.reflect.ConstantPool API causes the JVM in some cases to pre-resolve certain constant pool entries. This allows a user to call static methods or access static members without running the class initialization method, and may allow a user to observe uninitialized values.

## References
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://github.com/eclipse/openj9/issues/12016

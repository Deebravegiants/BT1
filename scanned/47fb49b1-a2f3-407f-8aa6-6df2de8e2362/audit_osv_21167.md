# [C] CVE-2021-41035

## Summary
Severity: Critical
Advisory: CVE-2021-41035
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-41035
Type: osv

## Details
In Eclipse Openj9 before version 0.29.0, the JVM does not throw IllegalAccessError for MethodHandles that invoke inaccessible interface methods.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=576395
- https://gitlab.eclipse.org/eclipsefdn/emo-team/emo/-/issues/104
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://github.com/eclipse-openj9/openj9/pull/13740

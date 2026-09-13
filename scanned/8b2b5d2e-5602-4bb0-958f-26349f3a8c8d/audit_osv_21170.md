# [M] CVE-2021-41041

## Summary
Severity: Medium
Advisory: CVE-2021-41041
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-04-27
Source: https://osv.dev/vulnerability/CVE-2021-41041
Type: osv

## Details
In Eclipse Openj9 before version 0.32.0, Java 8 & 11 fail to throw the exception captured during bytecode verification when verification is triggered by a MethodHandle invocation, allowing unverified methods to be invoked using MethodHandles.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=579744
- https://github.com/eclipse-openj9/openj9/pull/14935

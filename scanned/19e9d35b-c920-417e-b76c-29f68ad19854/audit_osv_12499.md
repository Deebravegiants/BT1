# [C] CVE-2018-12548

## Summary
Severity: Critical
Advisory: CVE-2018-12548
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2018-12548
Type: osv

## Details
In OpenJDK + Eclipse OpenJ9 version 0.11.0 builds, the public jdk.crypto.jniprovider.NativeCrypto class contains public static natives which accept pointer values that are dereferenced in the native code.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=543792

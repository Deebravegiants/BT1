# [H] CVE-2019-11770

## Summary
Severity: High
Advisory: CVE-2019-11770
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-14
Source: https://osv.dev/vulnerability/CVE-2019-11770
Type: osv

## Details
In Eclipse Buildship versions prior to 3.1.1, the build files indicate that this project is resolving dependencies over HTTP instead of HTTPS. Any of these artifacts could have been MITM to maliciously compromise them and infect the build artifacts that were produced. Additionally, if any of these JARs or other dependencies were compromised, any developers using these could continue to be infected past updating to fix this.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=547734
- https://github.com/eclipse/buildship/issues/855

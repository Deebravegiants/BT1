# [M] CVE-2019-3884

## Summary
Severity: Medium
Advisory: CVE-2019-3884
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2019-08-01
Source: https://osv.dev/vulnerability/CVE-2019-3884
Type: osv

## Details
A vulnerability exists in the garbage collection mechanism of atomic-openshift. An attacker able spoof the UUID of a valid object from another namespace is able to delete children of those objects. Versions 3.6, 3.7, 3.8, 3.9, 3.10, 3.11 and 4.1 are affected.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3884

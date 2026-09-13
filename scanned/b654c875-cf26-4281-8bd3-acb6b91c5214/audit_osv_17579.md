# [M] CVE-2020-1732

## Summary
Severity: Medium
Advisory: CVE-2020-1732
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/CVE-2020-1732
Type: osv

## Details
A flaw was found in Soteria before 1.0.1, in a way that multiple requests occurring concurrently causing security identity corruption across concurrent threads when using EE Security with WildFly Elytron which can lead to the possibility of being handled using the identity from another request.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1732
- https://github.com/wildfly-security/soteria/commit/c2479f8c39d7d661341fdcaff7f5e97c5eea1a54

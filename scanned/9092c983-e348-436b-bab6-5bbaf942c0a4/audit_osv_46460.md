# [M] CVE-2011-2910

## Summary
Severity: Medium
Advisory: CVE-2011-2910
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-15
Source: https://osv.dev/vulnerability/CVE-2011-2910
Type: osv

## Details
The AX.25 daemon (ax25d) in ax25-tools before 0.0.8-13 does not check the return value of a setuid call. The setuid call is responsible for dropping privileges but if the call fails the daemon would continue to run with root privileges which can allow possible privilege escalation.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-2910
- https://security-tracker.debian.org/tracker/CVE-2011-2910
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-2910
- https://access.redhat.com/security/cve/cve-2011-2910

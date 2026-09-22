# [M] CVE-2018-14650

## Summary
Severity: Medium
Advisory: CVE-2018-14650
CVSS: 5.0 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-09-27
Source: https://osv.dev/vulnerability/CVE-2018-14650
Type: osv

## Details
It was discovered that sos-collector does not properly set the default permissions of newly created files, making all files created by the tool readable by any local user. A local attacker may use this flaw by waiting for a legit user to run sos-collector and steal the collected data in the /var/tmp directory.

## References
- https://access.redhat.com/errata/RHSA-2018:3663
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14650
- https://github.com/sosreport/sos-collector/commit/72058f9253e7ed8c7243e2ff76a16d97b03d65ed

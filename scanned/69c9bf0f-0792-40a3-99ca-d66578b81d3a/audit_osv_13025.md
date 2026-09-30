# [M] CVE-2018-16888

## Summary
Severity: Medium
Advisory: CVE-2018-16888
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-14
Source: https://osv.dev/vulnerability/CVE-2018-16888
Type: osv

## Details
It was discovered systemd does not correctly check the content of PIDFile files before using it to kill processes. When a service is run from an unprivileged user (e.g. User field set in the service file), a local attacker who is able to write to the PIDFile of the mentioned service may use this flaw to trick systemd into killing other services and/or privileged processes. Versions before v237 are vulnerable.

## References
- https://lists.apache.org/thread.html/5960a34a524848cd722fd7ab7e2227eac10107b0f90d9d1e9c3caa74%40%3Cuser.cassandra.apache.org%3E
- https://access.redhat.com/errata/RHSA-2019:2091
- https://security.netapp.com/advisory/ntap-20190307-0007/
- https://usn.ubuntu.com/4269-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16888

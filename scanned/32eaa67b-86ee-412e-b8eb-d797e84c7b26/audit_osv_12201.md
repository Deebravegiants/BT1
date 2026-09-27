# [M] CVE-2018-10892

## Summary
Severity: Medium
Advisory: CVE-2018-10892
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-07-06
Source: https://osv.dev/vulnerability/CVE-2018-10892
Type: osv

## Details
The default OCI linux spec in oci/defaults{_linux}.go in Docker/Moby from 1.11 to current does not block /proc/acpi pathnames. The flaw allows an attacker to modify host's hardware like enabling/disabling bluetooth or turning up/down keyboard brightness.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00084.html
- https://access.redhat.com/errata/RHBA-2018:2796
- https://access.redhat.com/errata/RHSA-2018:2482
- https://access.redhat.com/errata/RHSA-2018:2729
- https://github.com/moby/moby/pull/37404
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10892

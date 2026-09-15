# [M] suddoers configuration for cscreen not restrictive enough

## Summary
Severity: Medium
Advisory: CVE-2022-21946
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2022-21946
Type: osv

## Details
A Incorrect Permission Assignment for Critical Resource vulnerability in the sudoers configuration in cscreen of openSUSE Factory allows any local users to gain the privileges of the tty and dialout groups and access and manipulate any running cscreen seesion. This issue affects: openSUSE Factory cscreen version 1.2-1.3 and prior versions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21946.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-21946
- https://bugzilla.suse.com/show_bug.cgi?id=1196451

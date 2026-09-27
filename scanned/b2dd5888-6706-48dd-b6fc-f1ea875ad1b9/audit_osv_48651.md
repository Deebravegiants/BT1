# [M] CVE-2018-10850

## Summary
Severity: Medium
Advisory: CVE-2018-10850
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-10850
Type: osv

## Details
389-ds-base before versions 1.4.0.10, 1.3.8.3 is vulnerable to a race condition in the way 389-ds-base handles persistent search, resulting in a crash if the server is under load. An anonymous attacker could use this flaw to trigger a denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00033.html
- https://access.redhat.com/errata/RHSA-2018:2757
- https://lists.debian.org/debian-lts-announce/2018/07/msg00018.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10850
- https://pagure.io/389-ds-base/issue/49768
- https://pagure.io/389-ds-base/c/8f04487f99a

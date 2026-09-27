# [M] CVE-2021-35937

## Summary
Severity: Medium
Advisory: CVE-2021-35937
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-35937
Type: osv

## Details
A race condition vulnerability was found in rpm. A local unprivileged user could use this flaw to bypass the checks that were introduced in response to CVE-2017-7500 and CVE-2017-7501, potentially gaining root privileges. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://access.redhat.com/security/cve/CVE-2021-35937
- https://rpm.org/wiki/Releases/4.18.0
- https://security.gentoo.org/glsa/202210-22
- https://bugzilla.redhat.com/show_bug.cgi?id=1964125
- https://www.usenix.org/legacy/event/sec05/tech/full_papers/borisov/borisov.pdf

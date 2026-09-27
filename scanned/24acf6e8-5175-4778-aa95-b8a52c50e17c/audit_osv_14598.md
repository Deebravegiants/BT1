# [M] CVE-2019-10206

## Summary
Severity: Medium
Advisory: CVE-2019-10206
Aliases: GHSA-cqmr-rcpr-cxh3, PYSEC-2019-145
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/CVE-2019-10206
Type: osv

## Details
ansible-playbook -k and ansible cli tools, all versions 2.8.x before 2.8.4, all 2.7.x before 2.7.13 and all 2.6.x before 2.6.19, prompt passwords by expanding them from templates as they could contain special characters. Passwords should be wrapped to prevent templates trigger and exposing them.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00026.html
- https://www.debian.org/security/2021/dsa-4950
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10206

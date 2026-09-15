# [H] CVE-2019-16729

## Summary
Severity: High
Advisory: CVE-2019-16729
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/CVE-2019-16729
Type: osv

## Details
pam-python before 1.0.7-1 has an issue in regard to the default environment variable handling of Python, which could allow for local root escalation in certain PAM setups.

## References
- https://tracker.debian.org/news/1066790/accepted-pam-python-107-1-source-amd64-all-into-unstable/
- https://usn.ubuntu.com/4552-1/
- https://usn.ubuntu.com/4552-2/
- https://www.debian.org/security/2019/dsa-4555
- https://lists.debian.org/debian-lts-announce/2019/11/msg00020.html
- https://bugzilla.suse.com/show_bug.cgi?id=1150510#c1
- https://sourceforge.net/p/pam-python/code/ci/0247ab687b4347cc52859ca461fb0126dd7e2ebe/

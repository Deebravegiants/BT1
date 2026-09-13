# [H] CVE-2020-26880

## Summary
Severity: High
Advisory: CVE-2020-26880
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-07
Source: https://osv.dev/vulnerability/CVE-2020-26880
Type: osv

## Details
Sympa through 6.2.57b.2 allows a local privilege escalation from the sympa user account to full root access by modifying the sympa.conf configuration file (which is owned by sympa) and parsing it through the setuid sympa_newaliases-wrapper executable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5CUVLHGWCDA6B2NH467ZMKL6O2NGLQZN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B5MFWWYY4TSQAXBWZ6SBFX43BLUL3WWI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E2TKOL454ZKKLQCUSUPNEZ52WELN4OAH/
- https://github.com/sympa-community/sympa/issues/1009
- https://github.com/sympa-community/sympa/issues/943#issuecomment-704779420
- https://github.com/sympa-community/sympa/issues/943#issuecomment-704842235
- https://lists.debian.org/debian-lts-announce/2020/11/msg00015.html

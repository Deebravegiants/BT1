# [H] CVE-2020-27828

## Summary
Severity: High
Advisory: CVE-2020-27828
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-27828
Type: osv

## Details
There's a flaw in jasper's jpc encoder in versions prior to 2.0.23. Crafted input provided to jasper by an attacker could cause an arbitrary out-of-bounds write. This could potentially affect data confidentiality, integrity, or application availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/COBEVDBUO3QTNR6YQBBTIQKNIB6W3MJ2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EBZZ2SNTQ4BSA6PNJCTOAKXIAXYNNF6V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N4ALB4SXHURLVWKAOKYRNJXPABW3M22M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPOVZTSIQPW2H4AFLMI3LHJEZGBVEQET/
- https://bugzilla.redhat.com/show_bug.cgi?id=1905201
- https://github.com/jasper-software/jasper/issues/252

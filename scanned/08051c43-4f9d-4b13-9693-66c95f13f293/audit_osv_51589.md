# [H] CVE-2021-3445

## Summary
Severity: High
Advisory: CVE-2021-3445
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-19
Source: https://osv.dev/vulnerability/CVE-2021-3445
Type: osv

## Details
A flaw was found in libdnf's signature verification functionality in versions before 0.60.1. This flaw allows an attacker to achieve code execution if they can alter the header information of an RPM package and then trick a user or system into installing it. The highest risk of this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DPMFGGQ5T6WVFTFX3OKMVTTM5O4EXWZR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G4NL7TNWAHJ6JVRABQUPWHKKCTHUZMNF/
- https://bugzilla.redhat.com/show_bug.cgi?id=1932079

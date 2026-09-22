# [H] CVE-2021-20271

## Summary
Severity: High
Advisory: CVE-2021-20271
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-20271
Type: osv

## Details
A flaw was found in RPM's signature check functionality when reading a package file. This flaw allows an attacker who can convince a victim to install a seemingly verifiable package, whose signature header was modified, to cause RPM database corruption and execute code. The highest threat from this vulnerability is to data integrity, confidentiality, and system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMGXO3W6DHPO62GJ4VVF5DEUX5DRUR5K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VHRPNBCRPDJHHQE3MBPSZK4H7X2IM7AC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YILPBTPSBRYL4POBI3F4YUSVPSOQNJBY/
- https://security.gentoo.org/glsa/202107-43
- https://www.starwindsoftware.com/security/sw-20220805-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1934125
- https://github.com/rpm-software-management/rpm/commit/d6a86b5e69e46cc283b1e06c92343319beb42e21

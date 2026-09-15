# [M] CVE-2021-3421

## Summary
Severity: Medium
Advisory: CVE-2021-3421
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-05-19
Source: https://osv.dev/vulnerability/CVE-2021-3421
Type: osv

## Details
A flaw was found in the RPM package in the read functionality. This flaw allows an attacker who can convince a victim to install a seemingly verifiable package or compromise an RPM repository, to cause RPM database corruption. The highest threat from this vulnerability is to data integrity. This flaw affects RPM versions before 4.17.0-alpha.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMGXO3W6DHPO62GJ4VVF5DEUX5DRUR5K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VHRPNBCRPDJHHQE3MBPSZK4H7X2IM7AC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YILPBTPSBRYL4POBI3F4YUSVPSOQNJBY/
- https://security.gentoo.org/glsa/202107-43
- https://bugzilla.redhat.com/show_bug.cgi?id=1927747

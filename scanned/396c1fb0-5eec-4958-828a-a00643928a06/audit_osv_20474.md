# [M] CVE-2021-3405

## Summary
Severity: Medium
Advisory: CVE-2021-3405
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-3405
Type: osv

## Details
A flaw was found in libebml before 1.4.2. A heap overflow bug exists in the implementation of EbmlString::ReadData and EbmlUnicodeString::ReadData in libebml.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JNHQI6MDOECJ2HT5GCLEX2DMJFEOWPW7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHIIMWZKHHELFF4NRDMOOCS3HKK3K4DF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YY7R2JZRO5I6WS62KTJFTZGKYELVFTVB/
- https://lists.debian.org/debian-lts-announce/2021/04/msg00016.html
- https://security.gentoo.org/glsa/202208-21
- https://github.com/Matroska-Org/libebml/issues/74

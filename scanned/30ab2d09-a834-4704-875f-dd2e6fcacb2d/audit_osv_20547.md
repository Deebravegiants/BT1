# [M] CVE-2021-3494

## Summary
Severity: Medium
Advisory: CVE-2021-3494
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2021-3494
Type: osv

## Details
A smart proxy that provides a restful API to various sub-systems of the Foreman is affected by the flaw which can cause a Man-in-the-Middle attack. The FreeIPA module of Foreman smart proxy does not check the SSL certificate, thus, an unauthenticated attacker can perform actions in FreeIPA if certain conditions are met. The highest threat from this flaw is to system confidentiality. This flaw affects Foreman versions before 2.5.0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1948005

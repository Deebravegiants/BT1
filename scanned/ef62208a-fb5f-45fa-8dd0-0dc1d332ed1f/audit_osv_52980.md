# [M] CVE-2022-2393

## Summary
Severity: Medium
Advisory: CVE-2022-2393
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-14
Source: https://osv.dev/vulnerability/CVE-2022-2393
Type: osv

## Details
A flaw was found in pki-core, which could allow a user to get a certificate for another user identity when directory-based authentication is enabled. This flaw allows an authenticated attacker on the adjacent network to impersonate another user within the scope of the domain, but they would not be able to decrypt message content.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2101046

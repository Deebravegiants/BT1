# [H] CVE-2020-14387

## Summary
Severity: High
Advisory: CVE-2020-14387
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-14387
Type: osv

## Details
A flaw was found in rsync in versions since 3.2.0pre1. Rsync improperly validates certificate with host mismatch vulnerability. A remote, unauthenticated attacker could exploit the flaw by performing a man-in-the-middle attack using a valid certificate for another hostname which could compromise confidentiality and integrity of data transmitted using rsync-ssl. The highest threat from this vulnerability is to data confidentiality and integrity. This flaw affects rsync versions before 3.2.4.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1875549

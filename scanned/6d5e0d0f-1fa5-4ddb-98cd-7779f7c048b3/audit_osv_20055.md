# [M] CVE-2021-29659

## Summary
Severity: Medium
Advisory: CVE-2021-29659
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-29659
Type: osv

## Details
ownCloud 10.7 has an incorrect access control vulnerability, leading to remote information disclosure. Due to a bug in the related API endpoint, the attacker can enumerate all users in a single request by entering three whitespaces. Secondary, the retrieval of all users on a large instance could cause higher than average load on the instance.

## References
- https://doc.owncloud.com/server/admin_manual/release_notes.html
- https://owncloud.com/security-advisories/cve-2021-29659/

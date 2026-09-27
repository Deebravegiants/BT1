# [M] CVE-2023-1055

## Summary
Severity: Medium
Advisory: CVE-2023-1055
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-27
Source: https://osv.dev/vulnerability/CVE-2023-1055
Type: osv

## Details
A flaw was found in RHDS 11 and RHDS 12. While browsing entries LDAP tries to decode the userPassword attribute instead of the userCertificate attribute which could lead into sensitive information leaked. An attacker with a local account where the cockpit-389-ds is running can list the processes and display the hashed passwords. The highest threat from this vulnerability is to data confidentiality.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZOYQ5TCV6ZEPMDV4CSLK3KINAAO4SRI/
- https://bugzilla.redhat.com/show_bug.cgi?id=2173517#c0

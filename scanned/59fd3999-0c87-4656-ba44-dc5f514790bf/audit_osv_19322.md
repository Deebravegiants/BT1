# [M] CVE-2021-20208

## Summary
Severity: Medium
Advisory: CVE-2021-20208
CVSS: 6.1 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-20208
Type: osv

## Details
A flaw was found in cifs-utils in versions before 6.13. A user when mounting a krb5 CIFS file system from within a container can use Kerberos credentials of the host. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2W4HSDIWXXNQBUW5ZS37RQMLJ7THK5AS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/66WJ3SVBHCSNQZAWSGLB6FBOCFU45FFG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z4BZSJXROEFHYATAAHHRR6P3HUSMPQB3/
- https://bugzilla.redhat.com/show_bug.cgi?id=1921116
- https://bugzilla.samba.org/show_bug.cgi?id=14651

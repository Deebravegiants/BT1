# [H] CVE-2021-3480

## Summary
Severity: High
Advisory: CVE-2021-3480
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-3480
Type: osv

## Details
A flaw was found in slapi-nis in versions before 0.56.7. A NULL pointer dereference during the parsing of the Binding DN could allow an unauthenticated attacker to crash the 389-ds-base directory server. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MXMOMPTZTGOVFOZUUNXHOVCAYIPST74W/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GVQCDRQRFHXVR3Z3FQYM3UMC7QZUDDRJ/
- https://bugzilla.redhat.com/show_bug.cgi?id=1944640

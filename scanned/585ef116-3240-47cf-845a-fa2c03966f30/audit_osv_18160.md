# [M] CVE-2020-24661

## Summary
Severity: Medium
Advisory: CVE-2020-24661
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-26
Source: https://osv.dev/vulnerability/CVE-2020-24661
Type: osv

## Details
GNOME Geary before 3.36.3 mishandles pinned TLS certificate verification for IMAP and SMTP services using invalid TLS certificates (e.g., self-signed certificates) when the client system is not configured to use a system-provided PKCS#11 store. This allows a meddler in the middle to present a different invalid certificate to intercept incoming and outgoing mail.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G7OTYTGND6EFOKNQJWCHKKXKSN7SM73Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NS6CSTOBVO5HSAR3X5CT6DS6QDHXDB26/
- https://tools.cisco.com/security/center/content/CiscoSeg/message/NS6CSTOBVO5HSAR3X5CT6DS6QDHXDB26/
- https://gitlab.gnome.org/GNOME/geary/-/issues/866

# [M] CVE-2020-8793

## Summary
Severity: Medium
Advisory: CVE-2020-8793
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-25
Source: https://osv.dev/vulnerability/CVE-2020-8793
Type: osv

## Details
OpenSMTPD before 6.6.4 allows local users to read arbitrary files (e.g., on some Linux distributions) because of a combination of an untrusted search path in makemap.c and race conditions in the offline functionality in smtpd.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OPH4QU4DNVHA7ACFXMYFCEP5PSXXPN4E/
- http://seclists.org/fulldisclosure/2020/Feb/28
- https://usn.ubuntu.com/4294-1/
- https://www.openbsd.org/security.html
- http://www.openwall.com/lists/oss-security/2020/02/24/4

# [M] CVE-2019-3870

## Summary
Severity: Medium
Advisory: CVE-2019-3870
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-3870
Type: osv

## Details
A vulnerability was found in Samba from version (including) 4.9 to versions before 4.9.6 and 4.10.2. During the creation of a new Samba AD DC, files are created in a private subdirectory of the install location. This directory is typically mode 0700, that is owner (root) only access. However in some upgraded installations it will have other permissions, such as 0755, because this was the default before Samba 4.8. Within this directory, files are created with mode 0666, which is world-writable, including a sample krb5.conf, and the list of DNS names and servicePrincipalName values to update.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6354GALK73CZWQKFUG7AWB6EIEGFMF62/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JTJVFA3RZ6G2IZDTVKLHRMX6QBYA4GPA/
- https://support.f5.com/csp/article/K20804356
- https://www.synology.com/security/advisory/Synology_SA_19_15
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3870
- https://bugzilla.samba.org/show_bug.cgi?id=13834
- https://www.samba.org/samba/security/CVE-2019-3870.html

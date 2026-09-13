# [H] CVE-2019-3878

## Summary
Severity: High
Advisory: CVE-2019-3878
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-26
Source: https://osv.dev/vulnerability/CVE-2019-3878
Type: osv

## Details
A vulnerability was found in mod_auth_mellon before v0.14.2. If Apache is configured as a reverse proxy and mod_auth_mellon is configured to only let through authenticated users (with the require valid-user directive), adding special HTTP headers that are normally used to start the special SAML ECP (non-browser based) can be used to bypass authentication.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNW5YMC5TLWVWNJEY6AIWNSNPRAMWPQJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X7NLAU7KROWNTHAYSA2S67X347F42L2I/
- https://access.redhat.com/errata/RHBA-2019:0959
- https://access.redhat.com/errata/RHSA-2019:0746
- https://access.redhat.com/errata/RHSA-2019:0766
- https://access.redhat.com/errata/RHSA-2019:0985
- https://usn.ubuntu.com/3924-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3878
- https://github.com/Uninett/mod_auth_mellon/pull/196

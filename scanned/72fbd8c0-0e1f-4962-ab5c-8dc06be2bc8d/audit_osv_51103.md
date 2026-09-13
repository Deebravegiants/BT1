# [C] CVE-2021-20314

## Summary
Severity: Critical
Advisory: CVE-2021-20314
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-20314
Type: osv

## Details
Stack buffer overflow in libspf2 versions below 1.2.11 when processing certain SPF macros can lead to Denial of service and potentially code execution via malicious crafted SPF explanation messages.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CMSFT2NJDZ7PATRZSQPAOGSE7JD6ELOB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GFXJRHPE5OSCPTNA3ZZ4ORDHT4JQH3Y4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y6T4HYXXSUQCGJB2ES6X7Q74YYF7V7XU/
- https://security.gentoo.org/glsa/202401-22
- https://bugzilla.redhat.com/show_bug.cgi?id=1993070

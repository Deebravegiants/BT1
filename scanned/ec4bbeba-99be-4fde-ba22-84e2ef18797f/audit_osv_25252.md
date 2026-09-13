# [M] Gvariant deserialisation does not match spec for non-normal data

## Summary
Severity: Medium
Advisory: CVE-2023-32665
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-14
Source: https://osv.dev/vulnerability/CVE-2023-32665
Type: osv

## Details
A flaw was found in GLib. GVariant deserialization is vulnerable to an exponential blowup issue where a crafted GVariant can cause excessive processing, leading to denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/09/msg00030.html
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-32665
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32665.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32665
- https://security.gentoo.org/glsa/202311-18
- https://security.netapp.com/advisory/ntap-20240426-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2211827
- https://gitlab.gnome.org/GNOME/glib/-/issues/2121

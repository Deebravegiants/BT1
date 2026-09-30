# [M] Libsoup: information disclosure may leads libsoup client sends authorization header to a different host when being redirected by a server

## Summary
Severity: Medium
Advisory: CVE-2025-46421
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-04-24
Source: https://osv.dev/vulnerability/CVE-2025-46421
Type: osv

## Details
A flaw was found in libsoup. When libsoup clients encounter an HTTP redirect, they mistakenly send the HTTP Authorization header to the new host that the redirection points to. This allows the new host to impersonate the user to the original host that issued the redirect.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:4439
- https://access.redhat.com/errata/RHSA-2025:4440
- https://access.redhat.com/errata/RHSA-2025:4508
- https://access.redhat.com/errata/RHSA-2025:4538
- https://access.redhat.com/errata/RHSA-2025:4560
- https://access.redhat.com/errata/RHSA-2025:4568
- https://access.redhat.com/errata/RHSA-2025:4609
- https://access.redhat.com/errata/RHSA-2025:4624
- https://access.redhat.com/errata/RHSA-2025:7436
- https://access.redhat.com/errata/RHSA-2025:7505
- https://access.redhat.com/security/cve/CVE-2025-46421
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46421.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46421
- https://bugzilla.redhat.com/show_bug.cgi?id=2361962
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/439
- https://gitlab.gnome.org/GNOME/libsoup

# [H] Yelp: yelp-xsl: overly permissive content security policy in yelp allows host file disclosure from flatpak applications

## Summary
Severity: High
Advisory: CVE-2026-13601
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13601
Type: osv

## Details
A flaw was found in Yelp due to an overly permissive Content Security Policy (CSP) implementation provided by yelp-xsl. A malicious Flatpak application can open crafted help content through the OpenURI portal. By embedding an untrusted CSS stylesheet within a structured SVG document, attacker-controlled content can bypass Flatpak's intended sandbox isolation, allowing Yelp to evaluate local XML inclusions and disclose arbitrary user-readable host files through remote CSS resource requests. This may result in the unauthorized disclosure of sensitive information.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/yelp/-/work_items/238
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-13601.json
- https://access.redhat.com/errata/RHSA-2026:47177
- https://access.redhat.com/errata/RHSA-2026:47178
- https://access.redhat.com/errata/RHSA-2026:54539
- https://access.redhat.com/errata/RHSA-2026:54540
- https://access.redhat.com/errata/RHSA-2026:54605
- https://access.redhat.com/errata/RHSA-2026:54624
- https://access.redhat.com/errata/RHSA-2026:54637
- https://access.redhat.com/errata/RHSA-2026:54666
- https://access.redhat.com/errata/RHSA-2026:57417
- https://access.redhat.com/security/cve/CVE-2026-13601
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13601.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13601
- https://bugzilla.redhat.com/show_bug.cgi?id=2494110
- https://gitlab.gnome.org/GNOME/yelp/-/commit/c8c8244c8a812860782d635890c9b6c43ecc2639
- https://blogs.gnome.org/mcatanzaro/2026/05/11/flatpak-sandbox-escape-via-yelp/

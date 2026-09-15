# [M] JLSEC-2026-1238

## Summary
Severity: Medium
Advisory: JLSEC-2026-1238
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/JLSEC-2026-1238
Type: osv

## Affected
- Julia: `XML2_jll` — affected >=0 <2.15.3+0

## Details
A flaw was found in libxml2, an XML parsing library. This uncontrolled recursion vulnerability occurs in the xmlCatalogXMLResolveURI function when an XML catalog contains a delegate URI entry that references itself. A remote attacker could exploit this configuration-dependent issue by providing a specially crafted XML catalog, leading to infinite recursion and call stack exhaustion. This ultimately results in a segmentation fault, causing a Denial of Service (DoS) by crashing affected applications.

## References
- https://access.redhat.com/errata/RHSA-2026:7519
- https://access.redhat.com/security/cve/CVE-2026-0990
- https://bugzilla.redhat.com/show_bug.cgi?id=2429959
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/1018

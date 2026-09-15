# [M] Gimp: gimp:memory disclosure and denial of service via specially crafted pcx image

## Summary
Severity: Medium
Advisory: CVE-2026-4887
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-4887
Type: osv

## Details
A flaw was found in GIMP. This issue is a heap buffer over-read in GIMP PCX file loader due to an off-by-one error. A remote attacker could exploit this by convincing a user to open a specially crafted PCX image. Successful exploitation could lead to out-of-bounds memory disclosure and a possible application crash, resulting in a Denial of Service (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:16484
- https://access.redhat.com/errata/RHSA-2026:17533
- https://access.redhat.com/errata/RHSA-2026:19362
- https://access.redhat.com/errata/RHSA-2026:20552
- https://access.redhat.com/errata/RHSA-2026:20553
- https://access.redhat.com/errata/RHSA-2026:20554
- https://access.redhat.com/errata/RHSA-2026:20691
- https://access.redhat.com/errata/RHSA-2026:25899
- https://access.redhat.com/errata/RHSA-2026:25901
- https://access.redhat.com/errata/RHSA-2026:25907
- https://access.redhat.com/errata/RHSA-2026:26168
- https://access.redhat.com/security/cve/CVE-2026-4887
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4887.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4887
- https://bugzilla.redhat.com/show_bug.cgi?id=2451669
- https://gitlab.gnome.org/GNOME/gimp/-/issues/15960

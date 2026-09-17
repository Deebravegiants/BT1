# [M] libxml2: Use after free in xmlParseInternalSubset via improper entity resolution handling

## Summary
Severity: Medium
Advisory: CVE-2026-6653
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N/E:P)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-6653
Type: osv

## Details
Use After Free in libxml2's xmlParseInternalSubset from GNOME libxml2 version 2.9.11 to 2.11.0 allows a remote attacker to cause a denial-of-service via maliciously crafted XML input with improper entity resolution handling.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6653.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6653
- https://bugs.launchpad.net/ubuntu/+source/libxml2/+bug/2141260
- https://gitlab.gnome.org/GNOME/libxml2/-/work_items/1058
- https://gitlab.gnome.org/GNOME/libxml2

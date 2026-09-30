# [M] Dhcpcd: dhcpcd infinite loop and out-of-bounds read via zero-length ipv6 nd option in router advertisement handling

## Summary
Severity: Medium
Advisory: CVE-2026-14258
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-14258
Type: osv

## Details
A flaw was found in dhcpcd's IPv6 Neighbor Discovery Router Advertisement processing. A specially crafted IPv6 Router Advertisement containing a zero-length Neighbor Discovery option can bypass validation during packet storage and later be reparsed without adequate validation, causing the parser to enter a non-advancing loop. Successful exploitation may result in excessive CPU consumption, leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:54210
- https://access.redhat.com/security/cve/CVE-2026-14258
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14258.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14258
- https://bugzilla.redhat.com/show_bug.cgi?id=2462305
- https://github.com/NetworkConfiguration/dhcpcd/issues/415
- https://github.com/NetworkConfiguration/dhcpcd/commit/75289ca

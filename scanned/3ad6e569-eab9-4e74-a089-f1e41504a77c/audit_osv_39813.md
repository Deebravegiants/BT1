# [H] Shelf has cross-organization IDOR: authenticated users could read/attach another workspace's assets, tags, custodians, bookings, QR codes and audit data

## Summary
Severity: High
Advisory: CVE-2026-47697
Aliases: GHSA-r46p-gfrp-xxgq
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47697
Type: osv

## Details
Shelf is a platform for tracking physical assets. Shelf is multi-tenant; data is isolated per organization (workspace). Prior to version 1.20.2, several endpoints accepted entity IDs from request input and `connect`-ed / read / updated them without verifying the IDs belonged to the caller's organization. An authenticated user in Org A who knew or obtained an ID belonging to Org B could act on Org B's data across organization boundaries (a cross-tenant IDOR). A loader-only restriction on personal-workspace bookings was also bypassable via a crafted POST. Version 1.20.2 patches the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47697.json
- https://github.com/Shelf-nu/shelf.nu/security/advisories/GHSA-r46p-gfrp-xxgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47697

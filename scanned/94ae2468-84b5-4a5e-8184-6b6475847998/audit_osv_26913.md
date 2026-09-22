# [H] Squid: dos against http and https

## Summary
Severity: High
Advisory: CVE-2023-5824
Aliases: GHSA-543m-w2m2-g255
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-5824
Type: osv

## Details
A flaw was found in Squid. The limits applied for validation of HTTP response headers are applied before caching. However, Squid may grow a cached HTTP response header beyond the configured maximum size, causing a stall or crash of the worker process when a large header is retrieved from the disk cache, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/09/msg00027.html
- https://access.redhat.com/errata/RHSA-2023:7465
- https://access.redhat.com/errata/RHSA-2023:7668
- https://access.redhat.com/errata/RHSA-2024:0072
- https://access.redhat.com/errata/RHSA-2024:0397
- https://access.redhat.com/errata/RHSA-2024:0771
- https://access.redhat.com/errata/RHSA-2024:0772
- https://access.redhat.com/errata/RHSA-2024:0773
- https://access.redhat.com/errata/RHSA-2024:1153
- https://access.redhat.com/security/cve/CVE-2023-5824
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5824.json
- https://github.com/squid-cache/squid/security/advisories/GHSA-543m-w2m2-g255
- https://nvd.nist.gov/vuln/detail/CVE-2023-5824
- https://security.netapp.com/advisory/ntap-20231130-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2245914

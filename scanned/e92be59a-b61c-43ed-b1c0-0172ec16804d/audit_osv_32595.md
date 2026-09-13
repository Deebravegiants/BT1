# [M] Libsoup: denial of service in server when client requests a large amount of  overlapping ranges with range header

## Summary
Severity: Medium
Advisory: CVE-2025-32907
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32907
Type: osv

## Details
A flaw was found in libsoup. The implementation of HTTP range requests is vulnerable to a resource consumption attack. This flaw allows a malicious client to request the same range many times in a single HTTP request, causing the server to use large amounts of memory. This does not allow for a full denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:4439
- https://access.redhat.com/errata/RHSA-2025:4440
- https://access.redhat.com/errata/RHSA-2025:4508
- https://access.redhat.com/errata/RHSA-2025:7436
- https://access.redhat.com/errata/RHSA-2025:8128
- https://access.redhat.com/errata/RHSA-2025:8292
- https://access.redhat.com/security/cve/CVE-2025-32907
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32907.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32907
- https://bugzilla.redhat.com/show_bug.cgi?id=2359342
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/428
- https://gitlab.gnome.org/GNOME/libsoup/

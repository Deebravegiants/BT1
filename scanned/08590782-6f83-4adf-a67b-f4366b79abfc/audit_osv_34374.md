# [M] Python-kdcproxy: remote dos via unbounded tcp upstream buffering

## Summary
Severity: Medium
Advisory: CVE-2025-59089
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-59089
Type: osv

## Details
If an attacker causes kdcproxy to connect to an attacker-controlled KDC server (e.g. through server-side request forgery), they can exploit the fact that kdcproxy does not enforce bounds on TCP response length to conduct a denial-of-service attack. While receiving the KDC's response, kdcproxy copies the entire buffered stream into a new
buffer on each recv() call, even when the transfer is incomplete, causing excessive memory allocation and CPU usage. Additionally, kdcproxy accepts incoming response chunks as long as the received data length is not exactly equal to the length indicated in the response
header, even when individual chunks or the total buffer exceed the maximum length of a Kerberos message. This allows an attacker to send unbounded data until the connection timeout is reached (approximately 12 seconds), exhausting server memory or CPU resources. Multiple concurrent requests can cause accept queue overflow, denying service to legitimate clients.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:21138
- https://access.redhat.com/errata/RHSA-2025:21139
- https://access.redhat.com/errata/RHSA-2025:21140
- https://access.redhat.com/errata/RHSA-2025:21141
- https://access.redhat.com/errata/RHSA-2025:21142
- https://access.redhat.com/errata/RHSA-2025:21448
- https://access.redhat.com/errata/RHSA-2025:21748
- https://access.redhat.com/errata/RHSA-2025:21806
- https://access.redhat.com/errata/RHSA-2025:21818
- https://access.redhat.com/errata/RHSA-2025:21819
- https://access.redhat.com/errata/RHSA-2025:21820
- https://access.redhat.com/errata/RHSA-2025:21821
- https://access.redhat.com/errata/RHSA-2025:22982
- https://access.redhat.com/security/cve/CVE-2025-59089
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59089.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59089
- https://bugzilla.redhat.com/show_bug.cgi?id=2393958
- https://github.com/latchset/kdcproxy/commit/c7675365aa20be11f03247966336c7613cac84e1
- https://github.com/latchset/kdcproxy/pull/68

# [H] Iperf3: iperf3 server accepts unbounded peer-controlled json parameters enabling remote denial of service via resource exhaustion

## Summary
Severity: High
Advisory: CVE-2026-71217
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-71217
Type: osv

## Details
A flaw was found in iperf3. A remote attacker can exploit this vulnerability by sending crafted control-channel JSON with oversized numeric parameters, such as `parallel` and `len`, which are not properly validated by the server. This improper input validation can lead to excessive stream and thread creation, as well as large buffer allocations, causing resource exhaustion. Consequently, this can result in a Denial of Service (DoS) on the affected iperf3 server.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:61257
- https://access.redhat.com/errata/RHSA-2026:61389
- https://access.redhat.com/errata/RHSA-2026:61680
- https://access.redhat.com/security/cve/CVE-2026-71217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71217.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71217
- https://bugzilla.redhat.com/show_bug.cgi?id=2460984
- https://github.com/esnet/iperf/commit/494dd377eca4689672becdf06a85158557db1586

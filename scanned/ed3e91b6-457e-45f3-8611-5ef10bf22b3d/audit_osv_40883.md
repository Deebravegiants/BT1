# [M] Unauthenticated Denial-of-Service via TLS SAN Stuffing in Rancher and cattle-cluster-agent

## Summary
Severity: Medium
Advisory: CVE-2026-55996
Aliases: GHSA-9jxv-832x-45q9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-55996
Type: osv

## Details
A denial-of-service vulnerability was identified in multiple TLS listeners in Rancher. Both the cattle-cluster-agent component running in downstream clusters and the Rancher server itself use the dynamiclistener library to serve TLS traffic. Without an effective CN filter configured, dynamiclistener automatically appended to each serving certificate any hostname presented via Server Name Indication (SNI) in incoming TLS requests.



An unauthenticated attacker with network access within the affected cluster could send a large number of TLS requests with distinct hostnames, causing the serving certificate to accumulate an unbounded number of Subject Alternative Names (SANs). Eventually, the certificate grows large enough that TLS handshakes fail with an excessive message size error, causing a denial of service on the affected listeners.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55996.json
- https://github.com/rancher/rancher/security/advisories/GHSA-9jxv-832x-45q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55996
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-55996

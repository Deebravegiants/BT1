# [M] Consul vulnerable to a denial of service in the native RPC listener

## Summary
Severity: Medium
Advisory: CVE-2026-87106
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-87106
Type: osv

## Details
Consul and Consul Enterprise are vulnerable to a denial of service in the native RPC listener that may allow an authenticated client to exhaust server memory before ACL authorization is evaluated. A client that can complete the internal RPC mTLS handshake may exploit this issue without holding a valid ACL token. This vulnerability (CVE-2026-87106) is fixed in Consul 2.0.4 and Consul Enterprise 1.21.18, 1.22.12 and 2.0.4.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-35-consul-vulnerable-to-a-denial-of-service-in-the-native-rpc-listener/77737
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87106.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-87106
- https://github.com/hashicorp/consul

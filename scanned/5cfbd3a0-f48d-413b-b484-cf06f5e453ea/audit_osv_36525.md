# [M] Unbounded memory allocation for DoQ and DoH3

## Summary
Severity: Medium
Advisory: CVE-2026-24030
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-24030
Type: osv

## Details
An attacker might be able to trick DNSdist into allocating too much memory while processing DNS over QUIC or DNS over HTTP/3 payloads, resulting in a denial of service. In setups with a large quantity of memory available this usually results in an exception and the QUIC connection is properly closed, but in some cases the system might enter an out-of-memory state instead and terminate the process.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24030.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24030
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-02.html
- https://github.com/PowerDNS/pdns

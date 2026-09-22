# [H] Denial of service via crafted DoH exchange

## Summary
Severity: High
Advisory: CVE-2025-30194
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-30194
Type: osv

## Details
When DNSdist is configured to provide DoH via the nghttp2 provider, an attacker can cause a denial of service by crafting a DoH exchange that triggers an illegal memory access (double-free) and crash of DNSdist, causing a denial of service.

The remedy is: upgrade to the patched 1.9.9 version.

A workaround is to temporarily switch to the h2o provider until DNSdist has been upgraded to a fixed version.

We would like to thank Charles Howes for bringing this issue to our attention.

## References
- http://www.openwall.com/lists/oss-security/2025/04/29/1
- https://repo.powerdns.com/
- https://www.vicarius.io/vsociety/posts/cve-2025-30194-detection-dnsdist-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-30194-mitigate-dnsdist-vulnerability
- https://dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2025-02.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30194.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30194
- https://github.com/PowerDNS/pdns

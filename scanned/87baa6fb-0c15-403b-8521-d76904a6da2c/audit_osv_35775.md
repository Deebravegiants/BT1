# [M] Denial of service via crafted push/pull gossip message in memberlist

## Summary
Severity: Medium
Advisory: CVE-2026-14362
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-14362
Type: osv

## Details
HashiCorp memberlist before version 0.6.0 is vulnerable to a denial-of-service issue in its push/pull state handling that may allow an attacker with network access to the gossip port to exhaust memory on a receiving node and cause the process to terminate. This vulnerability (CVE-2026-14362) is fixed in memberlist 0.6.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-18-memberlist-vulnerable-to-denial-of-service-via-gossip-message/77556
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14362.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-14362
- https://github.com/hashicorp/memberlist

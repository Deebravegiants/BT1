# [H] Potential memory exposure in dns-packet

## Summary
Severity: High
Advisory: GHSA-3wcq-x3mq-6r9p
CVE: CVE-2021-23386
CWE: CWE-200, CWE-908
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-3wcq-x3mq-6r9p
Type: github-advisory

## Affected
- npm: `dns-packet` — affected >=2.0.0 <5.2.2
- npm: `dns-packet` — affected >=0 <1.3.2

## Details
This affects the package dns-packet before versions 1.3.2 and 5.2.2. It creates buffers with allocUnsafe and does not always fill them before forming network packets. This can expose internal application memory over unencrypted network when querying crafted invalid domain names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23386
- https://github.com/mafintosh/dns-packet/commit/0d0d593f8df4e2712c43957a6c62e95047f12b2d
- https://github.com/mafintosh/dns-packet/commit/25f15dd0fedc53688b25fd053ebbdffe3d5c1c56
- https://hackerone.com/bugs?subject=user&amp%3Breport_id=968858
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1295719
- https://snyk.io/vuln/SNYK-JS-DNSPACKET-1293563

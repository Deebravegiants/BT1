# [H] Denial of Service in Packetbeat

## Summary
Severity: High
Advisory: GHSA-9q3g-m353-cp4p
CVE: CVE-2017-11480
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-9q3g-m353-cp4p
Type: github-advisory

## Affected
- Go: `github.com/elastic/beats` — affected >=0 <5.6.4
- Go: `github.com/elastic/beats` — affected >=6.0.0-alpha1 <6.0.0

## Details
Packetbeat versions prior to 5.6.4 and 6.0.0 are affected by a denial of service flaw in the PostgreSQL protocol handler. If Packetbeat is listening for PostgreSQL traffic and a user is able to send arbitrary network traffic to the monitored port, the attacker could prevent Packetbeat from properly logging other PostgreSQL traffic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11480
- https://github.com/elastic/beats/pull/5457
- https://github.com/elastic/beats/pull/5479
- https://github.com/elastic/beats/pull/5480
- https://github.com/elastic/beats/commit/aeca65779d573976981587ca1d1461399e1b59dd
- https://discuss.elastic.co/t/beats-5-6-4-security-update/106739
- https://github.com/elastic/beats
- https://pkg.go.dev/vuln/GO-2022-0643

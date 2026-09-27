# [H] CVE-2024-29862

## Summary
Severity: High
Advisory: CVE-2024-29862
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2024-29862
Type: osv

## Details
The Kerlink firewall in ChirpStack chirpstack-mqtt-forwarder before 4.2.1 and chirpstack-gateway-bridge before 4.0.11 wrongly accepts certain TCP packets when a connection is not in the ESTABLISHED state.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29862.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29862
- https://github.com/chirpstack/chirpstack-gateway-bridge/commit/0c1e80c9fa9f5d093ff62903caedad86ec4640b6
- https://github.com/chirpstack/chirpstack-mqtt-forwarder/commit/4fa9e6eaaec8c3ca49ebfbf6317572671f17700f

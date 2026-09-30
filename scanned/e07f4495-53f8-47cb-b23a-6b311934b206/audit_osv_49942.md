# [M] CVE-2019-5061

## Summary
Severity: Medium
Advisory: CVE-2019-5061
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-5061
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the hostapd 2.6, where an attacker could trigger AP to send IAPP location updates for stations, before the required authentication process has completed. This could lead to different denial of service scenarios, either by causing CAM table attacks, or by leading to traffic flapping if faking already existing clients in other nearby Aps of the same wireless infrastructure. An attacker can forge Authentication and Association Request packets to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0849

# [M] CVE-2019-5062

## Summary
Severity: Medium
Advisory: CVE-2019-5062
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-5062
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the 802.11w security state handling for hostapd 2.6 connected clients with valid 802.11w sessions. By simulating an incomplete new association, an attacker can trigger a deauthentication against stations using 802.11w, resulting in a denial of service.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0850

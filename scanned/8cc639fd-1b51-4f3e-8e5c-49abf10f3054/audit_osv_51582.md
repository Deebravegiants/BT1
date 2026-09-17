# [M] CVE-2021-34146

## Summary
Severity: Medium
Advisory: CVE-2021-34146
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-34146
Type: osv

## Details
The Bluetooth Classic implementation in the Cypress CYW920735Q60EVB does not properly handle the reception of continuous unsolicited LMP responses, allowing attackers in radio range to trigger a denial of service and restart (crash) of the device by flooding it with LMP_AU_Rand packets after the paging procedure.

## References
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf
- https://www.cypress.com/documentation/datasheets/cyw20735b1-single-chip-bluetooth-transceiver-wireless-input-devices
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf

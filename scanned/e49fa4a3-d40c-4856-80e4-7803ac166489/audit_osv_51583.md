# [M] CVE-2021-34147

## Summary
Severity: Medium
Advisory: CVE-2021-34147
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-34147
Type: osv

## Details
The Bluetooth Classic implementation in the Cypress WICED BT stack through 2.9.0 for CYW20735B1 does not properly handle the reception of a malformed LMP timing accuracy response followed by multiple reconnections to the link slave, allowing attackers to exhaust device BT resources and eventually trigger a crash via multiple attempts of sending a crafted LMP timing accuracy response followed by a sudden reconnection with a random BDAddress.

## References
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf
- https://www.cypress.com/documentation/datasheets/cyw20735b1-single-chip-bluetooth-transceiver-wireless-input-devices

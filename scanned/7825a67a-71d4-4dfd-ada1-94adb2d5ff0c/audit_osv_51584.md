# [M] CVE-2021-34148

## Summary
Severity: Medium
Advisory: CVE-2021-34148
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-34148
Type: osv

## Details
The Bluetooth Classic implementation in the Cypress WICED BT stack through 2.9.0 for CYW20735B1 devices does not properly handle the reception of LMP_max_slot with a greater ACL Length after completion of the LMP setup procedure, allowing attackers in radio range to trigger a denial of service (firmware crash) via a crafted LMP packet.

## References
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf
- https://www.cypress.com/documentation/datasheets/cyw20735b1-single-chip-bluetooth-transceiver-wireless-input-devices

# [M] CVE-2020-11683

## Summary
Severity: Medium
Advisory: CVE-2020-11683
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-14
Source: https://osv.dev/vulnerability/CVE-2020-11683
Type: osv

## Details
A timing side channel was discovered in AT91bootstrap before 3.9.2. It can be exploited by attackers with physical access to forge CMAC values and subsequently boot arbitrary code on an affected system.

## References
- https://github.com/linux4sam/at91bootstrap/commit/7753914c9a622c245f3a3cf2af5e24b6a9904213
- https://labs.f-secure.com/advisories/microchip-at91bootstrap/

# [M] CVE-2025-27579

## Summary
Severity: Medium
Advisory: CVE-2025-27579
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L)
Published: 2025-03-02
Source: https://osv.dev/vulnerability/CVE-2025-27579
Type: osv

## Details
In Bitaxe ESP-Miner before 2.5.0 with AxeOS, one can use an /api/system CSRF attack to update the payout address (aka stratumUser) for a Bitaxe Bitcoin miner, or change the frequency and voltage settings.

## References
- https://snotra.uk/axeos-csrf-vulnerability.html
- https://www.nobsbitcoin.com/bitaxe-firmware-esp-miner-v2-5-0/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27579.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27579
- https://github.com/skot/ESP-Miner/pull/637

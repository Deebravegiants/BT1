# [C] Sunshine improperly enforces pairing protocol request order

## Summary
Severity: Critical
Advisory: CVE-2024-51738
Aliases: GHSA-3hrw-xv8h-9499
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/CVE-2024-51738
Type: osv

## Details
Sunshine is a self-hosted game stream host for Moonlight. In 0.23.1 and earlier, Sunshine's pairing protocol implementation does not validate request order and is thereby vulnerable to a MITM attack, potentially allowing an unauthenticated attacker to pair a client by hijacking a legitimate pairing attempt. This bug may also be used by a remote attacker to crash Sunshine. This vulnerability is fixed in 2025.118.151840.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51738.json
- https://github.com/LizardByte/Sunshine/security/advisories/GHSA-3hrw-xv8h-9499
- https://nvd.nist.gov/vuln/detail/CVE-2024-51738
- https://github.com/LizardByte/Sunshine/commit/89f097ae65277d42b5d40163d09d92e412e6d7dd

# [M] CVE-2021-46873

## Summary
Severity: Medium
Advisory: CVE-2021-46873
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-01-29
Source: https://osv.dev/vulnerability/CVE-2021-46873
Type: osv

## Details
WireGuard, such as WireGuard 0.5.3 on Windows, does not fully account for the possibility that an adversary might be able to set a victim's system time to a future value, e.g., because unauthenticated NTP is used. This can lead to an outcome in which one static private key becomes permanently useless.

## References
- https://lists.zx2c4.com/pipermail/wireguard/2021-August/006916.html

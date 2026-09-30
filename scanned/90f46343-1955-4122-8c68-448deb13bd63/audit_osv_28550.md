# [H] CVE-2024-34446

## Summary
Severity: High
Advisory: CVE-2024-34446
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2024-34446
Type: osv

## Details
Mullvad VPN through 2024.1 on Android does not set a DNS server in the blocking state (after a hard failure to create a tunnel), and thus DNS traffic can leave the device. Data showing that the affected device was the origin of sensitive DNS requests may be observed and logged by operators of unintended DNS servers.

## References
- https://github.com/mullvad/mullvadvpn-app/blob/main/CHANGELOG.md
- https://github.com/mullvad/mullvadvpn-app/tags
- https://news.ycombinator.com/item?id=40247604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34446.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34446
- https://github.com/mullvad/mullvadvpn-app/commit/0c39306a40f426853d617e20d596942e41091f13
- https://mullvad.net/en/blog/dns-traffic-can-leak-outside-the-vpn-tunnel-on-android

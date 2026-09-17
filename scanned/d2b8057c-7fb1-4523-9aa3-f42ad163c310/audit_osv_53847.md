# [H] CVE-2023-28450

## Summary
Severity: High
Advisory: CVE-2023-28450
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-28450
Type: osv

## Details
An issue was discovered in Dnsmasq before 2.90. The default maximum EDNS.0 UDP packet size was set to 4096 but should be 1232 because of DNS Flag Day 2020.

## References
- https://capec.mitre.org/data/definitions/495.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6UQ6LKDTLSSD64TBIZ3XEKBM2SWC63VV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OU2ZT4ITSEOOR2CFBAHK4Z67KXJIEWQA/
- https://thekelleys.org.uk/dnsmasq/doc.html
- https://thekelleys.org.uk/gitweb/?p=dnsmasq.git%3Ba=blob%3Bf=CHANGELOG
- https://thekelleys.org.uk/gitweb/?p=dnsmasq.git%3Ba=commit%3Bh=eb92fb32b746f2104b0f370b5b295bb8dd4bd5e5
- https://lists.debian.org/debian-lts-announce/2024/11/msg00035.html

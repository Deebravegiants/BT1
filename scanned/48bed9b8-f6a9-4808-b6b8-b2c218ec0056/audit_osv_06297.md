# [H] BIT-libpython-2022-45061

## Summary
Severity: High
Advisory: BIT-libpython-2022-45061
Aliases: BIT-python-2022-45061, BIT-python-min-2022-45061, CVE-2022-45061, PSF-2022-10
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2022-45061
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.16

## Details
An issue was discovered in Python before 3.11.1. An unnecessary quadratic algorithm exists in one path when processing some inputs to the IDNA (RFC 3490) decoder, such that a crafted, unreasonably long name being presented to the decoder could lead to a CPU denial of service. Hostnames are often supplied by remote servers that could be controlled by a malicious actor; in such a scenario, they could trigger excessive CPU consumption on the client attempting to make use of an attacker-supplied supposed hostname. For example, the attack payload could be placed in the Location header of an HTTP response with status code 302. A fix is planned in 3.11.1, 3.10.9, 3.9.16, 3.8.16, and 3.7.16.

## References
- https://github.com/python/cpython/issues/98433
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2AOUKI72ACV6CHY2QUFO6VK2DNMVJ2MB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/35YDIWCUMWTMDBWFRAVENFH6BLB65D6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4WBZJNSALFGMPYTINIF57HAAK46U72WQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/63FS6VHY4DCS74HBTEINUDOECQ2X6ZCH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7WQPHKGNXUJC3TC3BDW5RKGROWRJVSFR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B3YI6JYARWU6GULWOHNUROSACT54XFFS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B4MYQ3IV6NWA4CKSXEHW45CH2YNDHEPH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BWJREJHWVRBYDP43YB5WRL3QC7UBA7BR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GTPVDZDATRQFE6KAT6B4BQIQ4GRHIIIJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IN26PWZTYG6IF3APLRXQJBVACQHZUPT2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JCDJXNBHWXNYUTOEV4H2HCFSRKV3SYL3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JTYVESWVBPD57ZJC35G5722Q6TS37WSB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KNE4GMD45RGC2HWUAAIGTDHT5VJ2E4O4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LKWAMPURWUV3DCCT4J7VHRF4NT2CFVBR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O67LRHDTJWH544KXB6KY4HMHQLYDXFPK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ORVCQGJCCAVLN4DJDTWGREFCUWXKQRML/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PLQ2BNZVBBAQPV3SPRU24ZD37UYJJS7W/

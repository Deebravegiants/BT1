# [C] Heap-based buffer overflow in ZBar

## Summary
Severity: Critical
Advisory: GHSA-mhp6-jvpx-2p4m
CVE: CVE-2023-40889
CWE: CWE-122, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-mhp6-jvpx-2p4m
Type: github-advisory

## Affected
- PyPI: `zbar` — affected >=0

## Details
A heap-based buffer overflow exists in the qr_reader_match_centers function of ZBar 0.23.90. Specially crafted QR codes may lead to information disclosure and/or arbitrary code execution. To trigger this vulnerability, an attacker can digitally input the malicious QR code, or prepare it to be physically scanned by the vulnerable scanner.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40889
- https://github.com/mchehab/zbar
- https://hackmd.io/@cspl/B1ZkFZv23
- https://lists.debian.org/debian-lts-announce/2023/12/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/25LZZQJGGZRPLKTRNRNOTAFQJIPS7WRP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DC7V5YCLCPB36J2KY6WLZCABFLBRB665

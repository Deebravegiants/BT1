# [H] CVE-2023-33297

## Summary
Severity: High
Advisory: CVE-2023-33297
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-22
Source: https://osv.dev/vulnerability/CVE-2023-33297
Type: osv

## Details
Bitcoin Core before 24.1, when debug mode is not used, allows attackers to cause a denial of service (e.g., CPU consumption) because draining the inventory-to-send queue is inefficient, as exploited in the wild in May 2023.

## References
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures
- https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-24.1.md
- https://x.com/123456/status/1711601593399828530
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33297.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F2EI7SAP4QP2AJYK2JVEOO4GJ6DOBSM5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H3CQY277NWXY3RFCZCJ4VKT2P3ROACEJ/
- https://nvd.nist.gov/vuln/detail/CVE-2023-33297
- https://github.com/bitcoin/bitcoin/issues/27586
- https://github.com/bitcoin/bitcoin/issues/27623
- https://github.com/dogecoin/dogecoin/issues/3243#issuecomment-1712575544
- https://github.com/bitcoin/bitcoin/pull/27610
- https://github.com/visualbasic6/drain

# [H] MaraDNS Integer Underflow Vulnerability in DNS Packet Decompression

## Summary
Severity: High
Advisory: CVE-2023-31137
Aliases: GHSA-58m7-826v-9c3c
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-31137
Type: osv

## Details
MaraDNS is open-source software that implements the Domain Name System (DNS). In version 3.5.0024 and prior, a remotely exploitable integer underflow vulnerability in the DNS packet decompression function allows an attacker to cause a Denial of Service by triggering an abnormal program termination.

The vulnerability exists in the `decomp_get_rddata` function within the `Decompress.c` file. When handling a DNS packet with an Answer RR of qtype 16 (TXT record) and any qclass, if the `rdlength` is smaller than `rdata`, the result of the line `Decompress.c:886` is a negative number `len = rdlength - total;`. This value is then passed to the `decomp_append_bytes` function without proper validation, causing the program to attempt to allocate a massive chunk of memory that is impossible to allocate. Consequently, the program exits with an error code of 64, causing a Denial of Service.

One proposed fix for this vulnerability is to patch `Decompress.c:887` by breaking `if(len <= 0)`, which has been incorporated in version 3.5.0036 via commit bab062bde40b2ae8a91eecd522e84d8b993bab58.

## References
- https://github.com/samboy/MaraDNS/blob/08b21ea20d80cedcb74aa8f14979ec7c61846663/dns/Decompress.c#L886
- https://lists.debian.org/debian-lts-announce/2023/06/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3VSMLJX25MXGQ6A7UPOGK7VPUVDESPHL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NB7LDZM5AGWC5BHHQHW6CP5OFNBBKFOQ/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31137.json
- https://github.com/samboy/MaraDNS/security/advisories/GHSA-58m7-826v-9c3c
- https://nvd.nist.gov/vuln/detail/CVE-2023-31137
- https://www.debian.org/security/2023/dsa-5441
- https://github.com/samboy/MaraDNS/commit/bab062bde40b2ae8a91eecd522e84d8b993bab58

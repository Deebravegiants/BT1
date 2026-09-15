# [H] CVE-2026-42483

## Summary
Severity: High
Advisory: CVE-2026-42483
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42483
Type: osv

## Details
A heap-based buffer overflow in the Kerberos hash parser in hashcat v7.1.2 allows an attacker to cause a denial of service or possibly execute arbitrary code via a crafted Kerberos hash file. The issue affects module_hash_decode in multiple Kerberos-related modules because account_info_len is calculated from untrusted delimiter positions without upper-bound validation before memcpy copies the data into a fixed-size account_info buffer.

## References
- https://gist.github.com/sgInnora/107f2eb20367e47d58c911e38d56a91f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42483.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42483

# [H] CVE-2018-20421

## Summary
Severity: High
Advisory: CVE-2018-20421
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-24
Source: https://osv.dev/vulnerability/CVE-2018-20421
Type: osv

## Details
Go Ethereum (aka geth) 1.8.19 allows attackers to cause a denial of service (memory consumption) by rewriting the length of a dynamic array in memory, and then writing data to a single memory location with a large index number, as demonstrated by use of "assembly { mstore }" followed by a "c[0xC800000] = 0xFF" assignment.

## References
- https://github.com/ethereum/go-ethereum/issues/18289

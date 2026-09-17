# [H] CVE-2021-37491

## Summary
Severity: High
Advisory: CVE-2021-37491
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/CVE-2021-37491
Type: osv

## Details
An issue discovered in src/wallet/wallet.cpp in Dogecoin Project Dogecoin Core 1.14.3 and earlier allows attackers to view sensitive information via CWallet::CreateTransaction() function.

## References
- https://github.com/bitcoin/bitcoin/commit/2fb9c1e6681370478e24a19172ed6d78d95d50d3
- https://github.com/dogecoin/dogecoin/issues/2279
- https://github.com/VPRLab/BlkVulnReport/blob/main/NDSS23_BlockScope.pdf
- https://github.com/dogecoin/dogecoin/blob/master/src/wallet/wallet.cpp#L2628-L2640

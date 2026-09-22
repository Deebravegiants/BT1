# [H] CVE-2021-37492

## Summary
Severity: High
Advisory: CVE-2021-37492
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/CVE-2021-37492
Type: osv

## Details
An issue discovered in src/wallet/wallet.cpp in Ravencoin Core 4.3.2.1 and earlier allows attackers to view sensitive information via CWallet::CreateTransactionAll() function.

## References
- https://github.com/RavenProject/Ravencoin/issues/1086
- https://github.com/bitcoin/bitcoin/commit/2fb9c1e6681370478e24a19172ed6d78d95d50d3
- https://github.com/RavenProject/Ravencoin/blob/master/src/wallet/wallet.cpp#L3657-L3671

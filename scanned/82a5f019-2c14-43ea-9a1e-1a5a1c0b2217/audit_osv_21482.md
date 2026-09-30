# [M] CVE-2021-43398

## Summary
Severity: Medium
Advisory: CVE-2021-43398
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-11-04
Source: https://osv.dev/vulnerability/CVE-2021-43398
Type: osv

## Details
Crypto++ (aka Cryptopp) 8.6.0 and earlier contains a timing leakage in MakePublicKey(). There is a clear correlation between execution time and private key length, which may cause disclosure of the length information of the private key. This might allow attackers to conduct timing attacks. NOTE: this report is disputed by the vendor and multiple third parties. The execution-time differences are intentional. A user may make a choice of a longer key as a tradeoff between strength and performance. In making this choice, the amount of information leaked to an adversary is of infinitesimal value

## References
- https://cryptopp.com
- https://github.com/weidai11/cryptopp/issues/1080#issuecomment-996492222
- https://github.com/weidai11/cryptopp/issues/1080

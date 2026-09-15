# [M] CVE-2021-31876

## Summary
Severity: Medium
Advisory: CVE-2021-31876
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-31876
Type: osv

## Details
Bitcoin Core 0.12.0 through 0.21.1 does not properly implement the replacement policy specified in BIP125, which makes it easier for attackers to trigger a loss of funds, or a denial of service attack against downstream projects such as Lightning network nodes. An unconfirmed child transaction with nSequence = 0xff_ff_ff_ff, spending an unconfirmed parent with nSequence <= 0xff_ff_ff_fd, should be replaceable because there is inherited signaling by the child transaction. However, the actual PreChecks implementation does not enforce this. Instead, mempool rejects the replacement attempt of the unconfirmed child transaction.

## References
- https://bitcoinops.org/en/newsletters/2021/05/12/
- https://bitcoinops.org/en/topics/replace-by-fee/
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures#CVE-2021-31876
- https://github.com/bitcoin/bitcoin
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2021-May/018893.html

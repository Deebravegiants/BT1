# [M] CVE-2024-55563

## Summary
Severity: Medium
Advisory: CVE-2024-55563
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-55563
Type: osv

## Details
Bitcoin Core through 27.2 allows transaction-relay jamming via an off-chain protocol attack, a related issue to CVE-2024-52913. For example, the outcome of an HTLC (Hashed Timelock Contract) can be changed because a flood of transaction traffic prevents propagation of certain Lightning channel transactions.

## References
- https://ariard.github.io
- https://bitcoincore.org
- https://delvingbitcoin.org/t/full-disclosure-transaction-relay-throughput-overflow-attacks-against-off-chain-protocols/1305
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures
- https://gnusha.org/pi/bitcoindev/CALZpt+EptER=p+P7VN3QAb9n=dODA9_LnR9xZwWpRsdAwedv=w@mail.gmail.com/T/#u
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55563.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55563

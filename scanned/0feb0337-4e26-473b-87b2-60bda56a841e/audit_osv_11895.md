# [M] CVE-2018-1000022

## Summary
Severity: Medium
Advisory: CVE-2018-1000022
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000022
Type: osv

## Details
Electrum Technologies GmbH Electrum Bitcoin Wallet version prior to version 3.0.5 contains a Missing Authorization vulnerability in JSONRPC interface that can result in Bitcoin theft, if the user's wallet is not password protected. This attack appear to be exploitable via The victim must visit a web page with specially crafted javascript. This vulnerability appears to have been fixed in 3.0.5.

## References
- https://electrum.org/#home
- https://bitcointalk.org/index.php?topic=2702103.0
- https://github.com/spesmilo/electrum/issues/3374
- https://www.reddit.com/r/Bitcoin/comments/7ooack/critical_electrum_vulnerability/

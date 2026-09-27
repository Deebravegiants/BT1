# [H] CVE-2020-26896

## Summary
Severity: High
Advisory: CVE-2020-26896
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-26896
Type: osv

## Details
Prior to 0.11.0-beta, LND (Lightning Network Daemon) had a vulnerability in its invoice database. While claiming on-chain a received HTLC output, it didn't verify that the corresponding outgoing off-chain HTLC was already settled before releasing the preimage. In the case of a hash-and-amount collision with an invoice, the preimage for an expected payment was instead released. A malicious peer could have deliberately intercepted an HTLC intended for the victim node, probed the preimage through a colluding relayed HTLC, and stolen the intercepted HTLC. The impact is a loss of funds in certain situations, and a weakening of the victim's receiver privacy.

## References
- https://gist.github.com/ariard/6bdeb995565d1cc292753e1ee4ae402d
- https://lists.linuxfoundation.org/pipermail/lightning-dev/2020-October/002855.html
- https://lists.linuxfoundation.org/pipermail/lightning-dev/2020-October/002857.html

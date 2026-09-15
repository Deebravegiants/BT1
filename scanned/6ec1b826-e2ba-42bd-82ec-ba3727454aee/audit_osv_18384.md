# [M] CVE-2020-26895

## Summary
Severity: Medium
Advisory: CVE-2020-26895
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-26895
Type: osv

## Details
Prior to 0.10.0-beta, LND (Lightning Network Daemon) would have accepted a counterparty high-S signature and broadcast tx-relay invalid local commitment/HTLC transactions. This can be exploited by any peer with an open channel regardless of the victim situation (e.g., routing node, payment-receiver, or payment-sender). The impact is a loss of funds in certain situations.

## References
- https://gist.github.com/ariard/fb432a9d2cd3ba24fdc18ccc8c5c6eb4
- https://lists.linuxfoundation.org/pipermail/lightning-dev/2020-October/002856.html
- https://lists.linuxfoundation.org/pipermail/lightning-dev/2020-October/002858.html

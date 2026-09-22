# [H] CVE-2021-3195

## Summary
Severity: High
Advisory: CVE-2021-3195
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3195
Type: osv

## Details
bitcoind in Bitcoin Core through 0.21.0 can create a new file in an arbitrary directory (e.g., outside the ~/.bitcoin directory) via a dumpwallet RPC call. NOTE: this reportedly does not violate the security model of Bitcoin Core, but can violate the security model of a fork that has implemented dumpwallet restrictions

## References
- https://github.com/bitcoin/bitcoin/issues/20866

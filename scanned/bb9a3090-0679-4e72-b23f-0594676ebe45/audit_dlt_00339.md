# [?] - Memory DoS using huge INV messages

## Summary
Severity: Unknown
Chain: Bitcoin
Component: Bitcoin Core
CVE: CVE-2024-52915
Source: https://bitcoincore.org/en/security-advisories/
Type: bitcoin-advisory

## Details
CVE-2024-52915 - Memory DoS using huge INV messages
Nodes would allocate up to 50 MB of memory per attacker sending a malicious INV message. A fix was released on June 3rd, 2020 in Bitcoin Core 0.20.0.

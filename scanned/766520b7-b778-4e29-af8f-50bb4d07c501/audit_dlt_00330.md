# [?] CVE-2018-17144

## Summary
Severity: Unknown
Chain: Bitcoin
Component: Bitcoin Core
CVE: CVE-2018-17144
Source: https://bitcoincore.org/en/security-advisories/
Type: bitcoin-advisory

## Details
CVE-2018-17144
).
A consensus failure where nodes running older software rejected a block that
newer software accepted due to an underlying database limit, causing a
network-wide chain split (
BIP
50
).
High
: Bugs with a significant impact on affected nodes or the network. These are
typically exploitable remotely under default configurations and can cause
widespread disruption.
Examples
A remotely triggerable crash that could take many nodes offline
(

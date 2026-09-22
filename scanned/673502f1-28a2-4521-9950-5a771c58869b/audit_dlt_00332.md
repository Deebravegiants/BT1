# [?] CVE-2024-52922

## Summary
Severity: Unknown
Chain: Bitcoin
Component: Bitcoin Core
CVE: CVE-2024-52922
Source: https://bitcoincore.org/en/security-advisories/
Type: bitcoin-advisory

## Details
CVE-2024-52922
).
Low
: Bugs that are challenging to exploit or have a minor impact on a nodeâs
operation. They might only be triggerable under non-default configurations or
from the local network, and do not pose an immediate or widespread threat.
Examples
A malformed
getdata
message could cause a peer connection to enter an
infinite loop, consuming CPU but not affecting the nodeâs ability to process
blocks or handle other peer connections
(

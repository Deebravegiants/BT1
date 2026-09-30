# [M] Admin Can Break All Functionality Through Weth Address

## Summary
Severity: Medium
Contest weight: 0.0893
Dataset id: 9984
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
On the protocol, almost all functionality is constructed through WETH address. However, if the admin is set to WETH address mistakenly, user could not claim through [Comptroller.sol#L1381](https://github.com/Plex-Engineer/lending-market-v2/blob/main/contracts/Comptroller.sol#L1381). Admin can break the protocol.

## Recommendation
Set WETH address through initializer or change it through governance.

The admin of the lending-market and LP will be cosmos-sdk governance, vis-a-vis, the community, as such it is expected that a malicious governance proposal will not be passed.

Similarly to findings about `admin` re-initializing contracts, the warden has shown how, because the WETH address can be changed, accounting and functionality of the protocol and it’s interactions (in this case emission of rewards and all lending operations triggering a transfer of “COMP”), can be bricked.

Because this is contingent on malicious governance, I believe Medium Severity to be appropriate.

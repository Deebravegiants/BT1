# [?] EL-2020-13: For a dynamically-sized storage-array with types of size at most 16 bytes, assignments that require deleting slots did not zero out the deleted slots properly.

## Summary
Severity: Unknown
Chain: Ethereum (execution layer)
Component: Go Ethereum
Source: https://github.com/ethereum/public-disclosures/blob/master/disclosures/EL-2021-12-01.md
Type: ef-disclosure

## Details
Affected Clients: Go Ethereum
Uid: EL-2020-13
Bug: For a dynamically-sized storage-array with types of size at most 16 bytes, assignments that require deleting slots did not zero out the deleted slots properly.
Links: [](https://solidity.ethereum.org/2020/10/07/solidity-dynamic-array-cleanup-bug/)[https://solidity.ethereum.org/2020/10/07/solidity-dynamic-array-cleanup-bug/](https://solidity.ethereum.org/2020/10/07/solidity-dynamic-array-cleanup-bug/)
Reported: 2020-10-04
Bounty Hunter: jtoman
Bounty Points: 2000

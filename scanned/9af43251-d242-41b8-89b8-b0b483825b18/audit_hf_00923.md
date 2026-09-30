# [M] replaceGovernanceContract is not reset

## Summary
Severity: Medium
Contest weight: 0.3988
Dataset id: 2778
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After the governance is replaced, the VotesGCByVault is not reset to 0. This can lead to a situation where if the governance for the vault is reverted back to a previous contract, the vote count is still recorded, allowing a guard to change it back without proper voting. For example, consider governance contracts A and B: A is voted to be replaced by B. If B has a problem or bug and is replaced back by A, the vote count for B is still recorded. A guard can then vote to change it back to B immediately without proper voting.
```solidity
@external
def replaceGovernance(NewGovernance: address, vault: address):
    #Add Vote to VoteCount
    for guard_addr in self.LGov:
        if self.VotesGCByVault[vault][guard_addr] == NewGovernance:
            VoteCount += 1
    if len(self.LGov) == VoteCount:
        AdapterVault(vault).replaceGovernanceContract(NewGovernance)
```

## Recommendation
Reset VotesGCByVault to 0.

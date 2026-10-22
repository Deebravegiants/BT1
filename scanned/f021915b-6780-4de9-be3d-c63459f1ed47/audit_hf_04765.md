# [M] The owner of the Steadefi LendingVaults can

## Summary
Severity: Medium
Contest weight: 0.2126
Dataset id: 22610
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Steadefi admin can permanently prevent Copra from withdrawing their assets by pausing their LendingVaults. As it can be seen, the Steadefi LendingVault has a function called emergencyShutdown, that is capable of pausing the contract at any given moment. The function has a limited access to only addresses that have the keeper role assigned to them. This role can only be assigned by the contract owner. Furthermore, what we can also see is that the withdraw function of the same contract is only executable when the contract is not paused. This is the only function that allows the withdrawal of assets from the LendingVault contracts. Taking a look at an arbitrary Steadefi LendingVault deployed on Arbitrum, we can also verify that the implementation details referred to above are indeed present in the contracts that are deployed on-chain. Finally, according to the contest README, external contract owners should not be able to prevent Copra from being able to always execute withdrawals: Q: In case of external protocol integrations, are the risks of external contracts pausing or executing an emergency withdrawal acceptable? If not, Watsons will submit issues related to these situations that can harm your protocol's functionality. Pausing is acceptable as long as we can always withdraw. What we can conclude from all of this information is that the admin/owner of the Steadefi LendingVaults has the ability to prevent the Copra protocol users from performing an action for an unbounded period of time, that should otherwise always be possible to perform. The users of Copra can be prevented from withdrawing their funds

## Recommendation
Reconsider whether you really want integrate with Steadefi, given the power that its admin has

# [M] Semantics of totalAllocatedTokens

## Summary
Severity: Medium
Source: https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L27
Type: audit-issue

## Details
It is unclear what the [totalAllocatedTokens](https://github.com/etherparty/FUEL-Contracts/blob/3717b751bb2fa57ae300776a93ee4d7d7beb2c07/contracts/FuelToken.sol#L27) state variable of `FuelToken` means. At the moment the crowdfund is finalized, this variable will get out of sync with the amount of tokens actually distributed, because the platform will have all of the remaining supply to sell. Consider removing the variable altogether, or calling `allocateTokens` when the final remaining tokens are transferred to the platform in `finalizeCrowdfund`.

_**Update:** The variable was removed in [86abce6](https://github.com/etherparty/FUEL-Contracts/commit/86abce6f47041c9328037673d422834138bcc395)._

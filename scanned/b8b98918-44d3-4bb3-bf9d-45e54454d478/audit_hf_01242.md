# [C] Incorrect token amount calculation in liquid unstaking leads to asset loss

## Summary
Severity: Critical
Contest weight: 0.5791
Dataset id: 5751
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquid_unstake() function incorrectly handles token amounts during the unstaking process, leading to potential asset loss. The root cause lies in two key areas:
1. Token Amount Mismatch: While liquid_stake() accepts GOLD token amount as user input, liquid_unstake() accepts reward tokens amount as user input. This inconsistency creates an asymmetric relationship between staking and unstaking operations.
2. Incorrect State Update: The function decrease config.liquid_amount by the reward token amount instead of the GOLD token amount. Since liquid_amount tracks the total GOLD tokens in the vault, this leads to incorrect accounting of the protocol's assets.
This vulnerability can be exploited by users to manipulate the exchange rate between GOLD and reward tokens, potentially draining the vault.

## Recommendation
The function should be modified to:
1. Use the input amount as GOLD currency to maintain consistency with the liquid_stake() function, adjusting calculations accordingly.
2. Update config.liquid_amount with the correct GOLD amount.
Here's the proposed fix:
```solidity
pub fn liquid_unstake(&mut self, amount: u64) -> Result<()> {
let (canonical_bump_pda, _canonical_bump) =
Pubkey::find_program_address(&[b"whitelist", &self.user.key.to_bytes()], &ID);
assert_eq!(canonical_bump_pda, self.whitelist.key());
let cpi_program = self.token_program.to_account_info();
let seeds = &[b"config".as_ref(), &[self.config.bump]];
let signer_seeds = &[&seeds[..]];
let cpi_accounts = Burn {
```

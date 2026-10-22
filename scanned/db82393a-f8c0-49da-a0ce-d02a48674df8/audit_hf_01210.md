# [C] Insufficient validations allow attackers to steal by increasing refundable fee amount without any transfer fees

## Summary
Severity: Critical
Contest weight: 0.4385
Dataset id: 5381
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The transfer_hook instruction is intended to be called by the Token2022 program on token transfers of supported mints. The instruction only checks that the transferring flag of the source account is true. This ensures that the Token2022 has called the transfer hook program corresponding to the source_token account's mint.
However, this does not guarantee that the caller of transfer_hook instruction is Token2022.
An attacker can create a new token and have the transfer hook program of the new token call the transfer_hook with their own accounts and parameters.
As a result, attacker can increase the AccountWhitelist::refundable_amount without transferring any Lingo tokens and later claim the refundable_amount amount of Lingo tokens.

## Proof of Concept
Eve, an attacker can do the following:
1. Eve deploys an Exploit program supporting transfer execute interface.
2. Eve creates a new token P with Transfer Fee and Transfer Hook extensions.
3. Eve sets the transfer hook program of P to her exploit program.
4. Eve mints P tokens to her accounts A and B.
5. Eve calls Token2022 to transfer tokens from A to B.
• Token2022 calls P transfer hook: the Exploit program.
– Token2022 sets transferring field of A and B to true.
• Exploit calls LingoToken's transfer_hook instruction i.e execute.
• source_token: A.
• mint: P.
• destination_token: B.
• owner: Eve.
• extra_account_meta_list: uninitialized PDA for the seeds.
• whitelist_account: Eve's whitelist account for the Lingo Token.
• token_program: Token2022.
• _amount argument: u64::MAX.
– The check_is_transferring function returns Ok(()) as A transferring flag is true.
– The transfer_hook function will compute the fee and add it to the Whitelist::refundable_amount.
6. Eve gets refundable_amount fee in LingoToken by transferring her own tokens.
Eve can set transfer fee and transfer amounts to large values to steal all accumulated fees.

## Recommendation
Check that the mint is a supported token i.e. the transfer_hook_program_id of the mint is LingoToken program id. This, along with source_token.transferring flag and source_token.mint == mint, guarantees that the caller is Token2022.
Additionally:
1. Add PDA address check for whitelist_account using #[account(mut, seeds = [...])].
2. Ensure extra_account_meta_list is initialized: assert u64(extra_account_meta_list.data[0:8]) != 0.

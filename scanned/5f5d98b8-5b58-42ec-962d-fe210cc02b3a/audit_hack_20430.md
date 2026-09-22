# [H] Neodyme: SPL Token-2022: Don't shoot yourself in the foot with extensions

## Summary
Severity: High
Published: Tue, 10 Sep 2024
Source: https://neodyme.io/en/blog/token-2022/
Type: security-research

## Details
Sep 10, 2024 ~21 min read 

## SPL Token-2022: Don't shoot yourself in the foot with extensions 

Authored by: - Mathias 

## TL;DR ¶ 

 We go through the new functionalites, potential security pitfalls, and best practices for secure implementation of the new token extensions.

## Introduction ¶ 

 The Solana Token Program is the backbone of token management on the Solana blockchain, handling the creation, transfer, and burning of tokens. It provides essentially the only infrastructure for all token-related activities on Solana.

 Token-2022 (a.k.a. Token Extensions) enhances and expands the capabilities of the original Token program, adding in more options and use cases for token creators.
The extension support introduces new features which users can benefit from, but also presents additional challenges and risks for developers.

 In this article, we present and discuss these extensions.
Join us as we explore these new functionalities and highlight new security pitfalls and footguns that arise.

## What Are Extensions? ¶ 

 An extension adds extra features to standard tokens, allowing developers to customize token functionality, such as adding transfer hooks or minting restrictions, without changing the core token program.
This flexibility enables more tailored token implementations on the Solana blockchain.

 Extensions can be applied to both mints and token accounts.

 Mint Extensions add extra functionality to the token mint and are controlled by the mint creator.
Mint extensions must be applied during the mint initialization process and cannot be changed afterwards.

 Account Extensions can be required by the mint (such as the account transfer fee extension) or enabled by the user.
Some account extensions can be added after the account initialization, but most cannot.

## Extension Pitfalls ¶ 

 If you’re developing a program with token-2022 support, there are a number of pitfalls you should be aware of.
Let’s go through the token extensions that are currently available and let’s see how they can affect the security of your program.

## CPIGuard (Account) ¶ 

 The CPIGuard extension enhances security by preventing accounts from being used within a CPI, stopping malicious contracts from forwarding signatures to loot accounts.
However, delegates can still use the token account within a CPI, maintaining the standard flow of approving third-party token use.

 This extension can be enabled or disabled on demand using the 
```
CpiGuardInstruction::Enable
```
 and 
```
CpiGuardInstruction::Disable
```
 instructions.

### Security Implications ¶ 

 With the CPIGuard activated on the token account, your program must follow the delegation flow to transfer the user’s tokens with a CPI call to another account.
This doesn’t pose any immediate danger to the program as long as the transfer is verified to be successful.

## Default Account State (Mint) ¶ 

 The Default Account State extension allows mints to predefine the state of a token account upon creation.
An account can be either frozen or initialized.
So far, freezing accounts by default could only be done rather incompletely via an off-chain monitoring bot that freezes relevant new accounts after observing their creation until certain conditions are met. This extension eliminates the need for (and the significant problems with) the bot approach.

 The default state for future accounts can be updated later by the mint’s freeze authority using the 
```
DefaultAccountStateInstruction::Update
```
 instruction if the use case changes.

### Security implications ¶ 

 Frozen newly created vault or escrow accounts can cause programs to malfunction. In certain conditions, when combined with a flawed transfer process implementation, this issue could even result in a loss of funds.

 A simple fix is to check if the new account is frozen and to adapt accordingly.

## Group Pointers (Mint) ¶ 

 The group pointer, like the metadata pointer , allows a token creator to designate a group account to describe the mint.
Instead of detailing token metadata, the group account provides configurations for grouping tokens.

 When a Token-2022 mint has a group pointer, it’s considered a group mint (e.g. a Collection NFT).
Group mints can serve as reference points for related sets of tokens.

 Similar to metadata pointers, the group pointer can point to the mint itself, and clients must verify that the mint and the group point to each other.

### Security Implications ¶ 

 No dangers arise from this extension, because it is solely cosmetic. Hence, for programs it is safe to support tokens with this extension.

## Interest Bearing Mint (Mint) ¶ 

 Tokens that fluctuate in value have various real-world applications, such as bonds.
Traditionally, achieving this with tokens required proxy contracts to perform regular rebase or update operations.

 However, the Token-2022 extension model changes how token amounts are represented in the UI.
By using the InterestBearingMint extension and the 
```
PodTokenInstruction::AmountToUiAmount
```
 instruction, you can set an interest rate on your token and fetch its amount with interest at any time.

 Interest is continuously compounded based on the network timestamp. Although network timestamp drift may occasionally result in lower accumulated interest than expected, this is a rare occurrence.

### Security Implications ¶ 

 No dangers arise from this extension, because it is solely cosmetic. Hence, for programs it is safe to support tokens with this extension.

## Memo Transfer (Account) ¶ 

 Traditional banking systems often require a memo for all transfers.
The Token-2022 program includes an extension to meet this requirement.
By enabling required memo transfers on your token account, all incoming transfers must have a memo instruction immediately before the transfer instruction.

 Note: This also applies in CPI contexts if a CPI is performed to log the memo before the transfer.

### Security Implications ¶ 

 Transactions that try to transfer to such an account without a memo simply revert. This would only be a problem if it fails a transaction that is part of a multi-transaction intent. However, if the program tries to transfer to an attacker-controlled accounts, the transfer can also be blocked by simply closing the account. Hence the introduction of this behaviour does not create any new security pitfalls.

## Metadata Pointer (Mint) ¶ 

 With the potential for multiple metadata programs, a mint can have various accounts claiming to describe it.

 With the metadata pointer extension, a token creator may designate an address for the canonical metadata, which can even be the mint itself.

 To prevent fake mints from posing as other mints, clients must verify that the mint and the metadata point to each other.

### Security Implications ¶ 

 No immediate dangers arise from this extension because it is solely cosmetic.
Hence, for programs it is safe to support tokens with this extension.

## Mint Close Authority (Mint) ¶ 

 In the old token program, mints couldn’t be closed, so rent couldn’t be reclaimed once the token had served its purpose.
With the “Mint Close Authority” extension, a mint creator may set an authority to close mint accounts.
However, there are checks to ensure that not just any mint can be closed:

- The close instruction must be signed by the close authority.

- The total supply of the mint must be 0.

 What happens to token accounts created for a mint when it gets closed?

 It turns out, nothing!
This means we can end up with token accounts for a mint that no longer exists.
While this isn’t inherently problematic, the Token-2022 program allows reinitializing a mint at the same address.
This can lead to a situation where orphan token accounts are associated with a different mint than they were originally created for.

 These token accounts won’t hold any value due to the zero supply restriction during mint closing, but this could cause extension incompatibilities.
The requirements of the new mint might not match the extensions activated on the old token accounts.

### Security Implications ¶ 

- 
 Unapproved accounts could transfer funds even if they’re not permitted to. For instance, a new mint freezes all new accounts upon initialization to ensure proper KYC by the mint creator. However, existing token accounts don’t require reinitialization, allowing them to bypass the KYC restriction.

- 
 Soulbound tokens aren’t truly soulbound. Consider a project that creates a new mint but forgets to add the 
```
NonTransferable
```
 extension. Before minting any tokens, they decide to close and correctly reinitialize the mint. Unfortunately, during this period, an attacker creates multiple token accounts and can now freely transfer these “soulbound” tokens or change the token account owners.

- 
 Transfer fee bypass is possible! Here’s how: a group of bad actors creates a mint without any extensions and sets up token accounts for themselves and their friends. They then close the mint and reinitialize it with a transfer fee. On the surface, this seems like a simple mistake corrected by reinitialization. However, with their original token accounts, created before any extensions were added, they can now transfer tokens without fees using the 
```
transfer
```
 instruction, while regular users must pay the fee. This is possible because the check for the Transfer Fee extension only happens on the source account.

 The solution is not that straightforward. If you support a mint in your protocol, check that it hasn’t been reinitialized at any point. Note that it isn’t enough to disallow Mints with the Closeable Mint extension - because it could be a Mint that used to be closeable, but has been reinitialized as non-closeable.

## Permanent Delegate (Mint) ¶ 

 A permanent delegate is a new authority stored in the mint that has unlimited access to tokens and accounts. This authority can transfer any amount of tokens from any account to another or even burn them. While this functionality is beneficial for adhering to jurisdictional requirements to seize assets, it also carries a significant potential for abuse.

### Security Implications ¶ 

 Losing your funds with this kind of extension is the obvious implication, especially for protocols with only one token account acting as a vault to store tokens for their users. While a mint owner may act according to regulations, your amazing swap pool could suddenly be out of funds because the authority didn’t just withdraw the bad actor’s share but drained it to zero.
Note that for swap pools, lending, cross-margin and similar protocols, the mint authority has similar power — checking that you trust both is essential.

 Check which mints you trust! If there is a permanent delegate present, ensure you trust the authorities controlling the mint. Additionally, verify that your program handles the situation properly if the token account is suddenly missing some tokens or is completely empty.

## Transfer Hook (Mint & Account) ¶ 

 The transfer hook extension is a powerful tool that allows a program defined by the mint authority to be called for each transfer. This program receives the involved token accounts and the transferred amount. All involved accounts are converted to read-only, and the sender’s signer privileges are dropped. To increase functionality, a transfer hook can specify additional accounts needed for the transfer, which must be added to the account list.

### Additional Accounts ¶ 

 Additional accounts for a hook can be defined in a special PDA seeded from 
```
[b"extra-account-metas" + mint.key]
```
 according to the data format defined in the TLV Account Resolution library .
Solana Labs offers Rust-based on-chain and off-chain helpers to assist with the additional account lookup, though it can still be a bit challenging.

### Use Cases ¶ 

 The ability to run any logic after each transfer opens up many possible use cases, such as:

- Restricting amounts to be transferred: Transfer hooks enable developers to restrict transfer amounts within a certain range, ensuring they don’t exceed defined minimum and/or maximum limits.

- Enforcing NFT royalties: Transfer hooks can ensure that NFT royalties are transferred within the same transaction as the NFT transfer.

- Blacklisting or whitelisting certain accounts: Transfer hooks have their own state, instructions, and authorities. This flexibility allows developers to add additional checks to transfers that are not possible with the standard token program.

 Of course, there are also many more use cases beyond the ones listed.

### Security Implications ¶ 

 While transfer hooks open up a vast number of possibilities, there are also some pitfalls to watch out for while you are developing your own transfer hooks.

 Verify mints 

 Because transfer hook programs can be called by any mint, you should restrict which mints your program supports by checking the mints present in the source and destination accounts.

 - 
```

```
 fn assert_is_valid_mint (ctx : & Context < TransferHook >) -> Result <()> { 

 let valid_mint = Pubkey :: from_str ( "Your_mint_pubkey" ) . unwrap (); 

 let source_token_info = ctx . accounts . source_token . to_account_info (); 

 let source_account_data_ref : Ref < &mut [ u8 ]> = source_token_info . try_borrow_data () ? ; 

 let source_account = PodStateWithExtensions :: < PodAccount > :: unpack ( * source_account_data_ref) ? ; 

 let destination_token_info = ctx . accounts . destination_token . to_account_info (); 

 let destination_account_data_ref : Ref < &mut [ u8 ]> = destination_token_info . try_borrow_data () ? ; 

 let destination_account = PodStateWithExtensions :: < PodAccount > :: unpack ( * destination_account_data_ref) ? ; 

 if source_account . base . mint != valid_mint || destination_account . base . mint != valid_mint { 

 return err! ( Error :: InvalidMint ); 

 } 

 Ok (()) 

 } 

```

```

 Of course, you can extend this check to take a list of supported mints. This list could be stored in a PDA owned by the transfer hook program and is modifiable by an authority defined by your program. Without this check, any mint could use your transfer hook and access the data in your PDAs if you don’t separate your PDAs by mints. If you intend to support multiple mints, ensure that you use the mint’s public key as part of the seeds.

 Verify transferring state 

 The token program always sets the 
```
transferring
```
 flag in all token accounts involved in the transfer to 
```
true
```
. This simple check ensures that a threat actor doesn’t call your transfer hook outside of a transfer.

```

```
 fn assert_is_transferring (ctx : & Context < TransferHook >) -> Result <()> { 

 let source_token_info = ctx . accounts . source_token . to_account_info (); 

 let source_account_data_ref : Ref < &mut [ u8 ]> = source_token_info . try_borrow_data () ? ; 

 let source_account = PodStateWithExtensions :: < PodAccount > :: unpack ( * source_account_data_ref) ? ; 

 let source_account_extension = source_account . get_extension :: < TransferHookAccount >() ? ; 

 let destination_token_info = ctx . accounts . destination_token . to_account_info (); 

 let destination_account_data_ref : Ref < &mut [ u8 ]> = destination_token_info . try_borrow_data () ? ; 

 let destination_account = PodStateWithExtensions :: < PodAccount > :: unpack ( * destination_account_data_ref) ? ; 

 let destination_account_extension = destination_account . get_extension :: < TransferHookAccount >() ? ; 

 if ! bool :: from (source_account_extension . transferring) 

 || ! bool :: from (destination_account_extension . transferring) 

 { 

 return err! ( TransferError :: IsNotCurrentlyTransferring ); 

 } 

 Ok (()) 

 } 

```

```

 Verify token account mints 

 While the previous two checks are effective, an attacker could still create their own mint and transfer hook, and then call your transfer hook from their hook. This way, they can pass a supported mint and some token accounts that don’t belong to the passed mint. To prevent this, not only should you check if the mint is supported and the token accounts are in the transferring state, but also verify that the passed token accounts belong to the mint.

```

```
 fn assert_is_valid_account (ctx : & Context < TransferHook >) -> Result <()> { 

 let source_token_info = ctx . accounts . source_token . to_account_info (); 

 let source_account_data_ref : Ref < &mut [ u8 ]> = source_token_info . try_borrow_data () ? ; 

 let source_account = PodStateWithExtensions :: < PodAccount > :: unpack ( * source_account_data_ref) ? ; 

 let destination_token_info = ctx . accounts . destination_token . to_account_info (); 

 let destination_account_data_ref : Ref < &mut [ u8 ]> = destination_token_info . try_borrow_data () ? ; 

 let destination_account = PodStateWithExtensions :: < PodAccount > :: unpack ( * destination_account_data_ref) ? ; 

 if source_account . base . mint != ctx . accounts . mint . key () 

 || destination_account . base . mint != ctx . accounts . mint . key () 

 { 

 return err! ( TransferError :: IsNotCurrentlyTransferring ); 

 } 

 Ok (()) 

 } 

```

```

 Verify the caller is Token-2022 

 A more restrictive measure is to verify that the current caller of the program is the Token-2022 program. While for most transfer hooks the first two checks are sufficient, it can be necessary to ensure that the caller is actually the token program itself.

```

```
 pub fn assert_cpi_program_is_token22 ( 

 instructions_program : & AccountInfo , 

 ) -> Result <()> { 

 let ix_relative = get_instruction_relative ( 0 , instructions_program) ? ; 

 if ix_relative . program_id != token_2022 :: ID { 

 return err! ( TransferError :: InvalidCpiTransferProgram . into ()); 

 } 

 Ok (()) 

 } 

```

```

 While this check is great and improves security, it prevents a transfer from happening within a CPI itself. The 
```
get_instruction_relative()
```
 function retrieves the instruction in which the transfer hook is called and checks if the 
```
program_id
```
 matches the Token-2022 program ID.

 Therefore, if your use case involves transfers within a CPI, this check would prevent it.

## Transfer Fees (Mint & Account) ¶ 

 Introducing transfer fees directly into the token program is a significant improvement. It enables developers to move away from the old pattern of unfreezing, transferring, and refreezing tokens.

 With each transfer, the fee is automatically withheld from the recipient account and deducted from the transferred amount. These fees can be collected by anyone into the mint account, where the fee authority can withdraw them. Alternatively, the fee authority can withdraw the fees directly from the token accounts.

 Transfer between Bob and Alice with a 0.5% fee

### Security Implications ¶ 

- 
 Incorrect amounts can end up within escrow accounts of contracts because the fee is deducted from the recipient’s received amount, not from the sender’s balance. Programs that don’t account for this will face calculation issues.
There are a few ways to resolve this, and we recommend the first option as the cleaner solution.

- First, precalculate the fee amount and use the new 
```
TransferCheckedWithFee
```
 instruction.

- Second, calculate the difference in your balance before and after the transfer and use it to determine the transfer fee.

- 
 Accounts cannot be closed as long as fees are held back within them. Each time an account receives a transfer, the fees accumulate in the 
```
withheld_amount
```
 property of the token account extension. An account cannot be closed if 
```
withheld_amount
```
 is not zero. To close an account, the fees must first be harvested to the mint using the 
```
TransferFeeInstruction::HarvestWithheldTokensToMint
```
 instruction. After this, the account can be closed.

## Immutable Owner (Account) ¶ 

 Typically, a token account owner is able to reassign ownership to another address.
While useful in certain use cases, this can results in an ATA not belonging to the address it was created for, defeating the purpose of ATAs and potentially causing confusion and bugs.

 This extension prevents the owner from reassigning ownership.
It can be initialized by the user/program that creates the account. The ATA program has been amended to use this extension for Token-2022 accounts from now on.

## Non-Transferable (Mint) ¶ 

 The NonTransferable mint extension enables “soul-bound” tokens that cannot be transferred to other accounts, ideal for achievements tied to a single person or account.

 Unlike simply issuing a token and freezing the account, this extension allows the owner to burn and close the account if desired.

### Security Implications ¶ 

 There are no major implications regarding security with this extension.

## Confidential transfers (Mint & Account) ¶ 

 For us, one of the most interesting newly introduced features is confidential transfers. By using Zk-Proofs combined with ElGamal and some basic AES, one can now transfer tokens without disclosing the amount of the transfer. As you probably guessed, this functionality is managed by extensions.

 First, the mint needs to enable confidential transfers, which can only be done when the mint is initialized. Upon initialization, the mint owner defines three settings for this extension:

 Authority 
The authority that can update the settings.

 Auto-approve new accounts 
Determines whether or not new accounts are automatically approved for confidential transfers. If set to 
```
false
```
, accounts need to be explicitly approved by the defined authority for confidential transfers.

 Auditor ElGamal public key 
For regulatory reasons, the confidential transfer extension supports a third-party ElGamal key to decrypt the transfer amounts. This public key can be defined by the authority and is enforced by code to be able to decrypt the transfer amounts if set.

### How Do Transfers Work? ¶ 

 To transfer tokens privately, you and the recipient must initialize the confidential transfer extension in your accounts and have been approved by the authority configured in the mint. After that, you can deposit tokens from your public balance to your confidential balance using the 
```
ConfidentialTransferInstruction::Deposit
```
 instruction. Although the deposit and withdrawal events reveal your confidential balance initially, after several transfers with various parties, it becomes increasingly difficult for third parties to track your actual confidential balance.

 For a confidential transfer to occur, you must use the 
```
ConfidentialTransferInstruction::Transfer
```
 instruction. It is not possible to use the standard transfer instruction due to the additional cryptographic checks necessary for confidential transfers.

 After the transfer, the recipient cannot immediately use the received tokens because they are not merged with the actual balance but are stored as a pending balance within the account. Each account has a user defined counter for the maximum number of transfers it can receive before the pending balance must be applied. The maximum value for counter is stored in the token account’s 
```
maximum_pending_balance_credit_counter
```
 property and can be set individually by the account owner.

 When the account owner wants to make the pending balance available, or if the 
```
pending_balance_credit_counter
```
 has reached the maximum, the owner must call the 
```
ConfidentialTransferInstruction::ApplyPendingBalance
```
 instruction. This action applies the pending balance to the available confidential balance and resets the 
```
pending_balance_credit_counter
```
 to 0.

 Confidential transfer and applying pending balance

### Confidential Instructions ¶ 

 The confidential transfer extension has more instructions than we can cover in this blog post. To give an overview of its functionality, we provide a short list of all the instructions and a description of what they are used for below:

 Instruction Description 

 InitializeMint Initializes the extension on the mint with the additional settings described above. 

 UpdateMint Allows the authority to update if token accounts are automatically approved and the auditor’s public key. 

 ConfigureAccount Initializes the extension on the provided token account. 

 ApproveAccount Approves a token account if automatic approval is disabled. 

 EmptyAccount Sets the balance of the token account to 0. This instruction must be called before the token account can be closed. 

 Deposit Deposits the given amount from the public balance to the confidential balance. 

 Withdraw Withdraws the given amount from the confidential balance to the public balance. 

 Transfer Transfers the given amount confidentially to the recipient. The auditor’s public key defined in the mint must be able to decrypt it. 

 ApplyPendingBalance Applies the received tokens from the pending balance to the available balance. 

 EnableConfidentialCredits Enables this account to be a recipient of confidential transfers. 

 DisableConfidentialCredits Disables this account from being a recipient of confidential transfers. 

 EnableNonConfidentialCredits Enables this account to be a recipient of non-confidential transfers. 

 DisableNonConfidentialCredits Disables this account from being a recipient of non-confidential transfers. 

 TransferWithSplitProofs Same as 
```
Transfer
```
 but with split Zk-proofs. 

### Security Implications ¶ 

- 
 An attacker can intentionally exceed your 
```
maximum_pending_balance_credit_counter
```
 and thus prevent you from receiving any more confidential transfers. This value is controlled by the user and can only be set during the initialization of the extension. Therefore, we recommend setting it to an appropriate level based on the number of incoming transfers you expect. However, setting this value too high increases the calculation time required to generate the necessary proofs to apply the pending balance. If you receive another transfer during the calculation of the proof, you need to start over. So, higher doesn’t necessarily mean better. It is difficult to say what good values for this are — from active usage of the extension, this will hopefully become clearer over time.

- 
 While the amounts are encrypted, a user can leak the amounts they received by applying the pending balance and immediately withdrawing after only receiving one transaction. This allows chain analysts to determine the transfer value and effectively removes the privacy feature of this extension.

## Confidential Transfer Fee (Mint) ¶ 

 Transfer fees for confidential transfers work similarly to those for non-confidential transfers. Mint creators must initialize the ConfidentialTransferFee during mint creation. The process remains largely the same: fees are held in the recipient account, and an extra authority can directly withdraw these fees to the fee recipient. Account holders transfer fees to the mint to close their account if 
```
harvest_to_mint_enabled
```
 is set to 
```
true
```
 in the mint configuration.

 The key difference is that for confidential transfers, fees are not deducted from the transferred amount. Instead, the fee amount must be separately included in the Zk-Proof used for the transfer.

### Security implications ¶ 

 We don’t see any immediate security implications in using this extension.

## Implementation Details for Supporting Token-2022 Tokens ¶ 

## Authorities ¶ 

 With the introduction of extensions, Solana Labs also introduced new authorities. This overview table should serve as a reference for which authorities have what powers, and how they could affect the security of your program or your tokens:

 Storage location Account Authority Capabilities 

 Base Mint mint_authority Set new mint authority, mint new tokens, withdraw excess lamports 

 Base Mint freeze_authority Update default account state, freeze or unfreeze an account 

 Confidential Transfer Ext. Mint authority Approve accounts, change auto-approval, change auditor’s public key 

 Confidential Transfer Ext. Mint auditor Decrypt confidential transfer amounts 

 Confidential Transfer Fee Ext. Mint authority Withdraw fees from accounts and mint, sending them to fee recipient 

 Mint Close Authority Ext. Mint close_authority Close the mint 

 Group Member Pointer Ext. Mint authority Update member address 

 Group Member Ext. Mint authority Update group address 

 Interest Bearing Config Ext. Mint rate_authority Update the interest rate 

 Metadata Pointer Ext. Mint authority Update the metadata address 

 TokenGroup Ext. Mint update_authority Update the group authority, initialize new members, update the group maximum size 

 Token Metadata Ext. Mint update_authority Update metadata fields and values, remove metadata fields 

 Transfer Fee Ext. Mint transfer_fee_config_authority Update transfer fee configuration 

 Transfer Fee Ext. Mint withdraw_withheld_authority Withdraw withheld amounts from accounts and mints 

 Transfer Hook Ext. Mint authority Update the transfer hook program 

 Permanent Delegate Ext. Mint delegate Transfer or burn any amount from any token account 

 Base Account owner Transfer tokens, initialize extensions, delegate a specific amount to another address, revoke a delegation, burn tokens, withdraw excess lamports 

 Base Account close_authority Close the account 

 Base Account delegate Transfer or burn the delegated amount 

 Each authority listed here can update to a new public key. The only exception is the auditor set in the confidential transfer extension.

## Account Type Detection ¶ 

 Until now, if you got an account managed by the Token Program, it was easy to detect the type of the account by checking its size. This is no longer possible due to extensions. Since a Mint or TokenAccount can have a variable number of extensions, they can exceed the size expected by current implementations that check the type of an account only by its length.

 There is one exception where it is still feasible to check the type of an account by its length: Multisigs are still guaranteed to be 355 bytes long.
You might wonder if a Mint or Token Account could also be 355 bytes, leading to a false positive. However, this is not possible. Token-2022 checks for that edge case and simply adds an additional byte to the account.

 To ensure that the given account is of a certain type, you need to unpack the account data as shown here:

```

```
 use spl_token_2022 :: { 

 extension :: PodStateWithExtensions , 

 pod :: PodMint 

 }; 

 pub fn unpack_mint (account_data : & [ u8 ]) -> PodStateWithExtensions <' _ , PodMint , > { 

 PodStateWithExtensions :: < PodMint > :: unpack (account_data) . unwrap () 

 } 

```

```

 This code would fail if the given account data is not a Mint. The same can be done for token accounts by replacing 
```
PodMint
```
 with 
```
PodAccount
```
.

## Checking the Presence of Extensions in an Account ¶ 

 After reading this blog post, you probably think that you should support mints only with certain extensions. If not, we suggest you reconsider ;)

 To help you with that endeavor, we created a small implementation to allowlist certain extensions.

```

```
 use spl_token_2022 :: { 

 extension :: { ExtensionType , PodStateWithExtensions }, 

 pod :: PodMint 

 }; 

 const ALLOWED_EXTENSION_TYPES : [ ExtensionType ; 1 ] = [ ExtensionType :: DefaultAccountState ]; 

 fn assert_mint_extensions (account_data : & [ u8 ]) -> Result <()>{ 

 let mint = PodStateWithExtensions :: < PodMint > :: unpack (account_data) . unwrap (); 

 let mint_extensions = mint . get_extension_types () . unwrap (); 

 if ! mint_extensions . iter () . all ( | item | ALLOWED_EXTENSION_TYPES . contains (item)) { 

 return err! ( Error :: InvalidMint ) 

 } 

 Ok (()) 

 } 

```

```

## Conclusion ¶ 

 The Token-2022 extensions introduce an array of new possibilities that greatly enhance the functionality of token transactions on Solana. However, with these advancements come certain pitfalls that developers must be aware of. Hopefully, this blog post has given you some insights and practical advice to help you implement and use Token-2022 and its extensions more securely. By understanding and mitigating the associated risks, you can fully leverage the power of Token2022 in your projects.

 Managing new functionality like this can be tricky. We recommend that you double-check special cases and functionality you’re not sure you understand fully. Let other developers read your code and see if they find mistakes or logic bugs. And finally, a professional audit won’t hurt either ;)

 On this page

 - TL;DR 

- Introduction 

- What Are Extensions? 

- Extension Pitfalls 

 - CPIGuard (Account) 

 - Security Implications 

- Default Account State (Mint) 

 - Security implications 

- Group Pointers (Mint) 

 - Security Implications 

- Interest Bearing Mint (Mint) 

 - Security Implications 

- Memo Transfer (Account) 

 - Security Implications 

- Metadata Pointer (Mint) 

 - Security Implications 

- Mint Close Authority (Mint) 

 - Security Implications 

- Permanent Delegate (Mint) 

 - Security Implications 

- Transfer Hook (Mint & Account) 

 - Additional Accounts 

- Use Cases 

- Security Implications 

- Transfer Fees (Mint & Account) 

 - Security Implications 

- Immutable Owner (Account) 

- Non-Transferable (Mint) 

 - Security Implications 

- Confidential transfers (Mint & Account) 

 - How Do Transfers Work? 

- Confidential Instructions 

- Security Implications 

- Confidential Transfer Fee (Mint) 

 - Security implications 

- Implementation Details for Supporting Token-2022 Tokens 

 - Authorities 

- Account Type Detection 

- Checking the Presence of Extensions in an Account 

- Conclusion 

 - Solana 

- Token-2022 

 Share:

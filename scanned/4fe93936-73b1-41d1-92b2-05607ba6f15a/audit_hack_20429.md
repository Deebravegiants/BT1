# [H] Neodyme: Riverguard: Mutation Rules for Finding Vulnerabilities

## Summary
Severity: High
Published: Wed, 28 May 2025
Source: https://neodyme.io/en/blog/riverguard_3_fuzzcases/
Type: security-research

## Details
May 28, 2025 ~14 min read 

## Riverguard: Mutation Rules for Finding Vulnerabilities 

Authored by: - Sebastian 

- Thomas 

 Welcome to the third blog post in our series on Riverguard, our
automated Solana smart contract vulnerability discovery tool. From our
 first post , you may
already know what Riverguard is and how it works:

- Riverguard automatically tests for exploitable bugs in ALL
programs currently deployed on Solana Mainnet — open-source or
not

- It does this by using transactions interacting with a smart contract
as a template for basic “fuzzing”

- The “fuzzing” consists of mutating and locally re-executing the
transactions in ways that uncover common vulnerabilities

- Riverguard has already uncovered numerous loss-of-funds bugs 
worth millions of dollars

 In our second
post , we told you
that we don’t exploit the vulnerabilities Riverguard finds. Instead,
we store them and make them available to the contracts’ developers —
you. You also saw how you can get access to these findings for your
own smart contract for free and with no setup on your part,
thanks to generous support from the Solana Foundation.

 In this third post, we’ll go through some of the basic mutation rules
(“fuzzcases”) that we’ve implemented so far. You’ll see how they work
and what kind of vulnerability they detect. Hopefully, you’ll come
away with a better understanding of how to interpret any potential
vulnerabilities Riverguard detects, as well as what kind of
vulnerabilities we still see quite often in the wild.

## Introduction ¶ 

 In this post, we’ll go through the following seven fuzzcases.

 Fuzzcase Description 

 Arbitrary Account Replaces the owner and key of an account while checking for unverified accounts 

 Create Account DoS Checks whether the program incorrectly uses 
```
create_account
```
 for creating accounts 

 Arbitrary Withdraw Removes the signature of a token transfer and determines if it succeeds nevertheless 

 Unchecked Token Vault Replaces the token recipient with the token source 

 Unchecked Invoke Signed Checks whether the program calls an unchecked program with added signatures 

 Unchecked Sigverify CPI Searches for an unchecked secp256k1 program invocation 

 Unchecked Instruction Sysvar Checks whether the program uses an unchecked instruction sysvar 

 They’re representative of some of the vulnerabilities we still see
quite often when auditing contracts, even though the underlying bug is
usually fairly basic. Indeed, we have dozens or even hundreds of hits
for most of these fuzzcases, showing that these vulnerability types
are far from a thing of the past.

## Fuzzcase Internals ¶ 

 Figure 1: Flow graph showing how Riverguard applies a fuzzcase to a transaction

 Once a transaction is fed into a fuzzcase, it usually follows the flow depicted in Figure 1:

 Step Example: Unchecked Token Vault 

 1. Checking the eligibility and applicability of the transaction Does an SPL transfer go from a user to a vault? 

 2. Modify the accounts to potentially trigger a bug Replace the token destination with the token source 

 3. Simulate the modified transaction - 

 4. Check whether the execution result indicates a bug Did the transfer still succeed? 

 5. False positive checks Is it a cranker instruction? 

 6. Log the bug in the database - 

 Subsequently, we either try a different mutation (if, for example, there are two SPL transfers in one transaction, we fuzz both), or we move on to the next fuzzcase.

 Now let’s see these fuzzcases and how they work in detail.

## Arbitrary Account ¶ 

 The Arbitrary Account fuzzcase tries to identify one of the most basic bugs found on
Solana:
 Missing account checks .

 - 
```

```
 fn process_instruction ( 

 program_id : & Pubkey , 

 accounts : & [ AccountInfo ], 

 instruction_data : & [ u8 ], 

 ) -> ProgramResult { 

 let account_info_iter = &mut accounts . iter (); 

 let assumed_state_acc = next_account_info (account_info_iter) ? ; 

 // MISSING: 

 // assumed_state_acc.owner == &program_id or 

 // assumed_state_acc.key == STATIC_KEY or 

 // some derivation check 

 // ... 

 let state = State :: try_from_slice ( & assumed_state_acc . data . borrow ()) ? ; 

 //... read values from state 

 } 

```

```

 The basic idea is as follows. If an instruction gets an account for
which neither the account key nor the owner is verified, that account
can be replaced by an attacker-controlled account with arbitrary
malicious data.

 We check this by looping over every non-executable, non-empty account
in a transaction, replacing its key and owner and rerunning the
transaction. If the modified transaction succeeds, the account was not
verified and is susceptible to an attack. Since this procedure by
itself is prone to many false positives, we conduct several more
checks. Let’s talk about those.

### False Positive Checking ¶ 

 The Riverguard framework offers the possibility to record the call
trace of a transaction execution. In other words, we are able to
inspect the current execution state after every instruction and CPI
invocation. In the Arbitrary Account fuzzcase, we record the accepted
accounts for every invocation. Then, we check whether the fuzzed call
trace is the same as the call trace of the unmodified transaction. If
this is not the case, there are probably some checks involved that
prevent our modified account from being used (e.g., a cranker
operating only on accounts that he owns).

 Secondly, we check whether the account is used at all. We replace the
accounts data with random data (while keeping the discriminator in
place). If the transaction still succeeds after this, the account is
probably not read at all and also isn’t prone to an attack.

 If neither of these two false positive checks are positive (hence, it’s likely to be a true positive), we log the
finding and report it to the central database.

 This fuzzcase corresponds to the Account Data
Matching 
and Owner
Checks 
examples in the Sealevel attacks repository.

## Create Account DoS ¶ 

 The Create Account DoS fuzzcase tackles a bug commonly found in Solana
programs. The System Program offers the possibility to create an
account using the 
```
SystemProgram::CreateAccount
```
 instruction. This
instruction allocates space for the account, transfers the
corresponding amount of rent and assigns the account to the new owner.

 A sample Rust code with this bug could look like this:

```

```
 pub fn create_pda ( 

 pda_account : & AccountInfo , 

 account_len : u64 , 

 program_id : & Pubkey , 

 initializer : & AccountInfo , 

 system_program : & AccountInfo , 

 seeds : & [ & [ & [ u8 ]]], 

 ) -> ProgramResult { 

 let rent = Rent :: get () ? ; 

 let rent_lamports = rent . minimum_balance (account_len); 

 invoke_signed ( 

 & system_instruction :: create_account ( 

 initializer . key, 

 pda_account . key, 

 rent_lamports, 

 account_len . try_into () . unwrap (), 

 program_id, 

 ), 

 & [ 

 initializer . clone (), 

 pda_account . clone (), 

 system_program . clone (), 

 ], 

 seeds, 

 ) ? ; 

 } 

```

```

 The problem here is that the instruction will fail if the account
already has a lamport balance greater than zero. Since anyone can
transfer lamports to any account, an attacker could block the creation
of the account if only CreateAccount is used, potentially causing a Denial of Service depending on the program context.

 This risk can be mitigated by splitting the CreateAccount operations
into separate allocate, transfer, and assign instructions, provided that
the account has > 0 lamports:

 Click to view code 
```

```
 if pda_account . lamports () > 0 { 

 let required_lamports = rent 

 . minimum_balance (space) 

 . max ( 1 ) 

 . saturating_sub (pda_account . lamports ()); 

 if required_lamports > 0 { 

 invoke ( 

 & system_instruction :: transfer (initializer . key, pda_account . key, required_lamports), 

 & [ 

 initializer . clone (), 

 pda_account . clone (), 

 system_program . clone (), 

 ], 

 ) ? ; 

 } 

 invoke_signed ( 

 & system_instruction :: allocate (pda_account . key, space as u64 ), 

 & [pda_account . clone (), system_program . clone ()], 

 & [seeds], 

 ) ? ; 

 invoke_signed ( 

 & system_instruction :: assign (pda_account . key, owner), 

 & [pda_account . clone (), system_program . clone ()], 

 & [seeds], 

 ) 

 } else { 

 invoke_signed ( 

 & system_instruction :: create_account ( 

 initializer . key, 

 pda_account . key, 

 rent . minimum_balance (space) . max ( 1 ), 

 space as u64 , 

 owner, 

 ), 

 & [ 

 initializer . clone (), 

 pda_account . clone (), 

 system_program . clone (), 

 ], 

 & [seeds], 

 ) 

 } 

```

```

 The fuzzcase for this is quite simple. First, we search for accounts that are
created in the instruction. Those are the accounts that have zero lamports
before the transaction, are not a signer in the top-level instruction (i.e., they are created as a PDA) and
have data after the transaction resumed.

 In the second phase, we simulate the transaction for every such
account with lamports set to greater than zero.

 A failure of the transaction indicates that the program is susceptible
to a DoS. As the false positives here strongly rely on the context of
the program (e.g., the DoSed account can be seeded arbitrarily), we do
not conduct any further checks here and simply report it as is. Please
keep this in mind if you find a Create Account incident in your
Riverguard view.

## Arbitrary Withdraw ¶ 

 The Arbitrary Withdraw fuzzcase tries to address a critical bug
pattern we have found in numerous contracts. In the
Withdraw instructions, the contract fails to verify that the
withdraw authority actually is a signer. In code, it could look like
this:

 Click to view code 
```

```
 fn withdraw ( 

 program_id : & Pubkey , 

 accounts : & [ AccountInfo ], 

 instruction_data : & [ u8 ], 

 ) -> ProgramResult { 

 let account_info_iter = &mut accounts . iter (); 

 let withdraw_authority = next_account_info (account_info_iter) ? ; 

 let token_vault_account = next_account_info (account_info_iter) ? ; 

 let token_vault_authority = next_account_info (account_info_iter) ? ; 

 let destination_account = next_account_info (account_info_iter) ? ; 

 let token_program = next_account_info (account_info_iter) ? ; 

 // MISSING: 

 // withdraw_authority.signer == true 

 let (token_vault_key, _) = 

 Pubkey :: find_program_address ([ b"vault" , withdraw_authority . as_ref ()], program_id); 

 assert_eq! (token_vault_key, token_vault_account . key); 

 let (_, token_vault_bump) = Pubkey :: find_program_address ( 

 [ b"vault_authority" , withdraw_authority . as_ref ()], 

 program_id, 

 ); 

 invoke_signed ( 

 & spl_token :: instruction :: transfer ( 

 token_program . key, 

 token_vault_account . key, 

 destination_account . key, 

 token_vault_authority . key, 

 & [token_vault_authority . key], 

 amount, 

 ) 

 . unwrap (), 

 & [ 

 token_program, 

 token_vault_authority, 

 token_vault_account, 

 destination_account, 

 ], 

 [ 

 b"vault_authority" , 

 withdraw_authority . as_ref (), 

 token_vault_bump, 

 ], 

 ) ? 

 } 

```

```

 We check this by first searching for a token instruction in which the source authority is not present as a signer in the transaction.
This
means that the instruction is signed by a PDA and therefore probably a
withdraw.

 Next, we mutate the transaction by removing all original signers and
replacing the previous token recipient with ourselves. If this
transaction still succeeds, it means that one can steal money.

 The fuzzcase itself is quite false positive-proof. The only
false-positive case we have ever found is the case of cranker
instructions refunding a small portion of SOL to incentivize crankers.

 In the Sealevel attacks repository, this would correspond to Example
0: Signer Authorization .

## Unchecked Token Vault ¶ 

 The Unchecked Token Vault fuzzcase addresses the following bug. In the
case of a 
```
Deposit
```
 Instruction, the contract does not verify that the
receiving account is actually correct. This means we could replace the
receiving token account with our own and still cause a liquidity token
(for example) to be minted.

 In code, the bug would look like this:

 Click to view code 
```

```
 fn deposit ( 

 program_id : & Pubkey , 

 accounts : & [ AccountInfo ], 

 instruction_data : & [ u8 ], 

 ) -> ProgramResult { 

 let account_info_iter = &mut accounts . iter (); 

 let source_token_account = next_account_info (account_info_iter) ? ; 

 let source_authority = next_account_info (account_info_iter) ? ; 

 let vault_account = next_account_info (account_info_iter) ? ; 

 let state_acc = next_account_info (account_info_iter) ? ; 

 let token_program = next_account_info (account_info_iter) ? ; 

 // MISSING: 

 // state.vault_account == vault_account 

 invoke ( 

 & spl_token :: instruction :: transfer ( 

 token_program . key, 

 source_token_account . key, 

 vault_account . key, 

 source_authority . key, 

 & [source_authority . key], 

 amount, 

 ) 

 . unwrap (), 

 & [ 

 token_program, 

 source_authority, 

 source_token_account, 

 vault_account, 

 ], 

 ) ? ; 

 state . balances[source_authority] += amount; 

 } 

```

```

 The first step in detecting the bug in Riverguard is the same as in
the Arbitrary Withdraw fuzzcase: we search for a token transfer.

 Then, we replace the token recipient with the token source account and
simulate the transaction. If the transfer still succeeds, we report a
finding.

 This fuzzcase is rather prone to false positives as there are many
programs such as arbitrage bots that don’t really hold or govern any
assets and therefore do not need a check for such a case. Please keep
this in mind if an Unchecked Token Vault finding is
reported for your contract.

## Unchecked Invoke Signed ¶ 

 Solana enables programs to interact with other programs through Cross
Program Invocations (CPI). This can be done using either 
```
invoke
```
 or

```
invoke_signed
```
 functions (although invoke just is a wrapper around

```
invoke_signed
```
, with no seeds passed). In the context of

```
invoke_signed
```
, a program can include seeds for a Program Derived
Address (PDA), which are then passed on as signers in the called
program:

```

```
 pub fn invoke_program ( 

 program_account : & AccountInfo , 

 authority : & AccountInfo , 

 authority_seeds : & [ & [ & [ u8 ]]], 

 <other accounts and params> 

 ) -> ProgramResult { 

 // MISSING: 

 // program_account.key == program::id() 

 invoke_signed ( 

 & program :: instruction_x ( 

 authority : authority, 

 <other accounts and params> 

 ), 

 & [ 

 authority . clone (), 

 program_account . clone (), 

 <other accounts> . clone (), 

 ], 

 authority_seeds, 

 ) ? ; 

 } 

```

```

 In most scenarios, it’s crucial to verify that the program being
called (here just 
```
program_account
```
) is indeed the intended one. If
this is not done, there could be a malicious attacker who inserts its
own program and might exploit some funds or functionality with the
added PDA signature.

 This is where the Unchecked Invoke Signed fuzzcase comes into
play. Riverguard introduces a feature that permits the monitoring of
every new CPI call and inspection of the current state. The fuzzcase
operates by iterating through each CPI-called program, substituting a
NOOP (no operation) program and then simulating the mutated
transaction.

 Should the NOOP program be executed with new signatures that were not
present initially, this is flagged as a finding.

 There are some cases where an attacker cannot further exploit the
signature — if, for example, it cannot call other programs like the
Token program with which it could leverage the signature into
something useful.

 This bug can also be found in the Sealevel attacks repository at
 Example 5: Arbitrary
CPI 

## Unchecked Instruction Sysvar ¶ 

 The Unchecked Instruction Sysvar fuzzcase seeks to protect from the
bug that caused one of the biggest hacks in Solana history, the
Wormhole Hack. The bug is found in the use of the Instruction
sysvar. Solana instructions can inspect their surrounding instructions
by using the Instruction sysvar. At this time, it is crucial to check
that the assumed sysvar pubkey is actually

```
Sysvar1nstructions1111111111111111111111111
```
. Otherwise, an attacker
could replace the assumed instruction data with its own manipulated
instructions:

```

```
 fn process_instruction ( 

 program_id : & Pubkey , 

 accounts : & [ AccountInfo ], 

 instruction_data : & [ u8 ], 

 ) -> ProgramResult { 

 let account_info_iter = &mut accounts . iter (); 

 let instruction_sysvar = next_account_info (account_info_iter) ? ; 

 // MISSING: 

 // instruction_sysvar.key == instructions::id() 

 let data = instruction_sysvar . data . borrow () 

 // now deprecated, use `load_instruction_at_checked` instead, 

 // which does the check automatically 

 let first_ix = instructions :: load_instruction_at ( 0 , data); 

 ... 

 } 

```

```

 The fuzzcase basically just replaces the sysvar key, simulates the
transaction and checks if it still succeeds. If it does, we run it
again with an empty sysvar to check if the instruction sysvar is read
at all. If both these checks are positive, we report a finding.

 Look at the code of Example
10 
of the Sealavel attacks repository for further information about this
bug.

## Unchecked Sigverify CPI ¶ 

 The unchecked Sigverify CPI fuzzcase is somewhat similar to the
Instruction Sysvar fuzzcase. Solana offers the possibility to verify a
secp256k1 signature using the native secp256k1 program at

```
KeccakSecp256k11111111111111111111111111111
```
. A user can insert data,
signature and pubkey into the program’s instruction data, and it will
succeed if the signature is valid and fail if it is not.

 At a later stage, a program can inspect the previous instructions
using the Instruction Sysvar and verify whether the expected data,
signature and pubkey match, thereby assuming the signature is valid:

```

```
 fn process_instruction ( 

 program_id : & Pubkey , 

 accounts : & [ AccountInfo ], 

 instruction_data : & [ u8 ], 

 ) -> ProgramResult { 

 let account_info_iter = &mut accounts . iter (); 

 let instruction_sysvar = next_account_info (account_info_iter) ? ; 

 let secp_ix = instructions :: load_instruction_at_checked ( 0 , & instruction_sysvar); 

 // MISSING: 

 // secp_ix.program_id == solana_program::secp256k1_program::id() 

 let secp_data_len = secp_ix . data . len (); 

 if secp_data_len < 2 { 

 return Err ( InvalidSecpInstruction . into ()); 

 } 

 let sig_len = secp_ix . data[ 0 ]; 

 ... 

 } 

```

```

 It is, of course, important to verify that the expected secp256k1
program key is the correct one.

 The fuzzcase seeks to find this case and replaces the secpk256k1
program key with a random key while keeping the data intact. If the
execution still succeeds, we report a finding.

## Deduplication of Findings ¶ 

 Imagine encountering a “Self Transfer” bug in one of your program’s
instructions. Whenever a transaction triggers this bug, it is flagged
by Riverguard. However, there is an issue: the accounts and
instruction data usually vary since different users interact with the
program using different parameters. This means that we must build some
sort of deduplication system to triage the overwhelming load of
reported bugs and their associated storage needs efficiently.

 We have addressed this issue by devising a heuristic method to group
and filter potential bugs. For each transaction, we generate a hash
using the following parameters:

- 
```
program_id
```

- 
```
fuzzcase_id
```

- 
```
instruction discriminator
```
 (for which we generate three distinct hashes based
on discriminator sizes of 1, 4, and 8 bytes)

- fuzzcase-specific data

 If the transaction’s hash already exists in the database, we simply
update the count of findings and the most recent discovery date
without storing the complete transaction data. Otherwise, we create a
new entry in the database.

 While this heuristic method has proven to be quite effective, there’s
still a risk of overlooking transactions that might represent new
bugs. For instance, if there are two distinct “Self Transfer” bugs
within the same instruction that only trigger under different input
parameters, our system might inadvertently miss one.

## Summary ¶ 

 We hope this deep-dive into these fuzzcases will help you understand
and navigate your Riverguard findings. We are keen on eliminating all
findings generated by Riverguard, which should mitigate the most
common and straightforward vulnerabilities in all deployed and
utilized smart contracts.

 For this project, we partnered with the Solana Foundation to offer
this service free of charge. If you haven’t done it yet, you can now
register for your Riverguard account on
 riverguard.io .

 Riveguard is one of our largest projects to date. However, while
Riverguard is powerful, it cannot replace a comprehensive security
audit. Its capabilities are limited to common problems that can be
detected on-chain and depend on the volume of transactions associated
with your smart contract. If your contract hasn’t seen significant
traffic, Riverguard may not be able to detect potential issues.

 We hope Riverguard will make your smart contracts more secure, as it
is an excellent first layer of protection. Nonetheless, if you are
looking for a more in-depth security audit, we are here to assist
you. Having found the largest number of loss-of-funds bugs both in
Solana itself and in Solana smart contracts, we believe we host the
best auditors on Solana. Contact us via contact@neodyme.io to set up
an audit, or to talk smart contract security.

 On this page

 - Introduction 

- Fuzzcase Internals 

 - Arbitrary Account 

- Create Account DoS 

- Arbitrary Withdraw 

- Unchecked Token Vault 

- Unchecked Invoke Signed 

- Unchecked Instruction Sysvar 

- Unchecked Sigverify CPI 

- Deduplication of Findings 

- Summary 

 - Riverguard 

- Solana 

 Share:

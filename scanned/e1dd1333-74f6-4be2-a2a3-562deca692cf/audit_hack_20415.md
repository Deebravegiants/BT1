# [H] OtterSec: Solana: the hidden dangers of lamport transfers

## Summary
Severity: High
Published: Wed, 14 May 2025
Source: https://osec.io/blog/king-of-the-sol/
Type: security-research

## Details
## Solana: the hidden dangers of lamport transfers

 Nicola Vella May 14, 2025 #solana Solanaâs lamport transfer logic hides dangerous edge cases â from rent-exemption quirks to write-demotion traps. We dissect a deceptively simple smart contract game to expose how transfers to arbitrary accounts can silently fail, brick your program, or crown an eternal king.

## Introduction 

 Is it safe to transfer lamports to an arbitrary address on Solana? The answer might surprise you.

 In this post, we explore a deceptively simple smart contract game inspired by King of the Ether . Through it, weâll highlight subtle pitfalls in Solanaâs account model that can brick your program â especially when it comes to transferring lamports.

## The game: King of the SOL 

 The game works like this:

- Anyone can become the king by bidding at least 2Ã the previous bid.

- The old king is reimbursed 95% of their bid.

- The remaining 5% goes into a prize pot.

- If the reigning king survives for 10 days without being dethroned, they can claim the entire pot.

 Simple, right?

 This is the core logic:

```

```
 1

 #[ derive ( Accounts )] 

 2

 pub struct ChangeKing < 'info > { 

 3

 #[ account ( mut )] 

 4

 pub throne : Account < 'info , Throne >, 

 5

 6

 /// CHECK: old_king gets a 95% refund, so ensure it's writable. 

 7

 #[ account ( mut , constraint = old_king . key () == throne . king )] 

 8

 pub old_king : AccountInfo < 'info >, 

 9

 10

 /// CHECK: any writable account is allowed as a new king. 

 11

 #[ account ( mut )] 

 12

 pub new_king : AccountInfo < 'info >, 

 13

 14

 #[ account ( mut )] 

 15

 pub payer : Signer < 'info >, 

 16

 } 

 17

 18

 #[ program ] 

 19

 pub mod king_of_the_sol { 

 20

 pub fn change_king ( ctx : Context < ChangeKing >, bid_amount : u64 ) -> Result <()> { 

 21

 // Check that bid_amount is at least 2x last_bid_amount 

 22

 assert! ( bid_amount >= ctx . accounts . throne . last_bid_amount * 2 ); 

 23

 transfer_from_signer ( 

 24

 & ctx . accounts . payer , 

 25

 & ctx . accounts . throne . to_account_info (), 

 26

 bid_amount , 

 27

 )?; 

 28

 29

 // Reimburse 95% of the last bid to the old king 

 30

 let to_reimburse = ( ctx . accounts . throne . last_bid_amount * 9500 ) / 10000 ; 

 31

 transfer_from_pda ( 

 32

 & ctx . accounts . throne . to_account_info (), 

 33

 & ctx . accounts . old_king , 

 34

 to_reimburse , 

 35

 )?; 

 36

 37

 // Set new king 

 38

 ctx . accounts . throne . king = ctx . accounts . new_king . key (); 

 39

 ctx . accounts . throne . last_bid_amount = bid_amount ; 

 40

 ctx . accounts . throne . last_time = Clock :: get ()?. unix_timestamp as u64 ; 

 41

 42

 Ok (()) 

 43

 } 

 44

 } 

```

```

 { #[account(mut)] pub throne: Account , /// CHECK: old_king gets a 95% refund, so ensure it's writable. #[account(mut, constraint = old_king.key() == throne.king)] pub old_king: AccountInfo , /// CHECK: any writable account is allowed as a new king. #[account(mut)] pub new_king: AccountInfo , #[account(mut)] pub payer: Signer ,}#[program]pub mod king_of_the_sol { pub fn change_king(ctx: Context , bid_amount: u64) -> Result { // Check that bid_amount is at least 2x last_bid_amount assert!(bid_amount >= ctx.accounts.throne.last_bid_amount * 2); transfer_from_signer( &ctx.accounts.payer, &ctx.accounts.throne.to_account_info(), bid_amount, )?; // Reimburse 95% of the last bid to the old king let to_reimburse = (ctx.accounts.throne.last_bid_amount * 9500) / 10000; transfer_from_pda( &ctx.accounts.throne.to_account_info(), &ctx.accounts.old_king, to_reimburse, )?; // Set new king ctx.accounts.throne.king = ctx.accounts.new_king.key(); ctx.accounts.throne.last_bid_amount = bid_amount; ctx.accounts.throne.last_time = Clock::get()?.unix_timestamp as u64; Ok(()) }}"> 

 Note this comment:

 any writable account is allowed as a new king.

 â¦Is our assumption correct?

## The bugs lurking beneath 

## Bug 1: the rent-exemption trap 

 On Solana, all accounts must maintain a minimum balance of lamports to remain rent-exempt. Specifically, an account can be in one of two states:

- Uninitialized : 
```
lamports = 0
```

- Initialized : 
```
lamports >= rent-exempt threshold
```

 This rent model exists to prevent low-cost DoS attacks on validators. The key idea is that even an account with no data (i.e., zero-length data buffer) still consumes on-chain resources; specifically, account metadata like its public key, owner, or lamport balance. That metadata must be stored persistently by validators, and that storage isnât free.

 So âpersistent stateâ on Solana doesnât just mean your programâs data â it includes the base account structure itself. Even accounts with 
```
 data . len () == 0 
```
 must meet a minimum rent threshold to remain alive and avoid garbage collection by the runtime.

 This is enforced at the runtime level; the relevant logic lives in 
```
svm_rent_collector.rs
```
 :

 svm_rent_collector.rs 
```

```
 117

 fn transition_allowed (& self , pre_rent_state : & RentState , post_rent_state : & RentState ) -> bool { 

 118

 match post_rent_state { 

 119

 RentState :: Uninitialized | RentState :: RentExempt => true , 

 120

 RentState :: RentPaying { 

 121

 data_size : post_data_size , 

 122

 lamports : post_lamports , 

 123

 } => { 

 124

 match pre_rent_state { 

 125

 RentState :: Uninitialized | RentState :: RentExempt => false , 

 126

 RentState :: RentPaying { 

 127

 data_size : pre_data_size , 

 128

 lamports : pre_lamports , 

 129

 } => { 

 130

 // Cannot remain RentPaying if resized or credited. 

 131

 post_data_size == pre_data_size && post_lamports <= pre_lamports 

 132

 } 

 133

 } 

 134

 } 

 135

 } 

 136

 } 

```

```

 bool { match post_rent_state { RentState::Uninitialized | RentState::RentExempt => true, RentState::RentPaying { data_size: post_data_size, lamports: post_lamports, } => { match pre_rent_state { RentState::Uninitialized | RentState::RentExempt => false, RentState::RentPaying { data_size: pre_data_size, lamports: pre_lamports, } => { // Cannot remain RentPaying if resized or credited. post_data_size == pre_data_size && post_lamports 

 You can check the rent-exemption threshold for a zero-data account with the CLI:

 Terminal window 
```

```
 solana rent 0 

 Rent-exempt minimum: 0.00089088 SOL 

```

```

### Fix 1: only reimburse if rent-exempt 

 We donât want to donate anything to an unfair king! So letâs update our program to reimburse only if the old king will be rent-exempt after the transfer:

```

```
 1

 let to_reimburse = ( ctx . accounts . throne . last_bid_amount * 9500 ) / 10000 ; 

 2

 let rent = Rent :: get ()?; 

 3

 let balance_after = ctx . accounts . old_king . lamports () + to_reimburse ; 

 4

 if rent . is_exempt ( balance_after , ctx . accounts . old_king . data_len ()) { 

 5

 transfer_from_pda ( 

 6

 & ctx . accounts . throne . to_account_info (), 

 7

 & ctx . accounts . old_king , 

 8

 to_reimburse , 

 9

 )?; 

 10

 } 

```

```

 But is rent-exemption the only thing that can cause a lamport transfer to fail? Not quite.

## Bug 2: writable but untouchable â 
```
set_lamports
```
 fails 

 Letâs look at 
```
BorrowedAccount::set_lamports
```
 :

 transaction-context/src/lib.rs 
```

```
 1

 /// Overwrites the number of lamports of this account (transaction wide) 

 2

 #[ cfg ( not ( target_os = "solana" ))] 

 3

 pub fn set_lamports (& mut self , lamports : u64 ) -> Result <(), InstructionError > { 

 4

 // An account not owned by the program cannot have its balance decrease 

 5

 if ! self . is_owned_by_current_program () && lamports < self . get_lamports () { 

 6

 return Err ( InstructionError :: ExternalAccountLamportSpend ); 

 7

 } 

 8

 // The balance of read-only may not change 

 9

 if ! self . is_writable () { 

 10

 return Err ( InstructionError :: ReadonlyLamportChange ); 

 11

 } 

 12

 // The balance of executable accounts may not change 

 13

 if self . is_executable_internal () { 

 14

 return Err ( InstructionError :: ExecutableLamportChange ); 

 15

 } 

 16

 // don't touch the account if the lamports do not change 

 17

 if self . get_lamports () == lamports { 

 18

 return Ok (()); 

 19

 } 

 20

 self . touch ()?; 

 21

 self . account . set_lamports ( lamports ); 

 22

 Ok (()) 

 23

 } 

 24

 25

 /// Feature gating to remove `is_executable` flag related checks 

 26

 #[ cfg ( not ( target_os = "solana" ))] 

 27

 #[ inline ] 

 28

 fn is_executable_internal (& self ) -> bool { 

 29

 ! self 

 30

 . transaction_context 

 31

 . remove_accounts_executable_flag_checks 

 32

 && self . account . executable () 

 33

 } 

```

```

 Result { // An account not owned by the program cannot have its balance decrease if !self.is_owned_by_current_program() && lamports bool { !self .transaction_context .remove_accounts_executable_flag_checks && self.account.executable()}"> 

 Turns out: even writable, rent-exempt accounts can still reject lamport transfers.

 Specifically, executable accounts cannot receive or send lamports â the runtime treats them as immutable.

 Note (Whatâs the executable flag anyway?) The 
```
executable
```
 flag is a legacy mechanism marking accounts that hold program code. Historically, an account with this flag was assumed to either contain immutable BPF bytecode or to be a proxy to a built-in program, and therefore it made sense to consider it read-only for performance reasons.

 This behavior became problematic with the introduction of the Upgradeable BPF Loader . A workaround was used to maintain compatibility with the existing runtime logic. The program data containing BPF bytecode was split into a separate account, ProgramData, with the program account now only containing an address pointing to the ProgramData account:

```

```
 1

 Program { 

 2

 /// Address of the ProgramData account. 

 3

 programdata_address : Pubkey , 

 4

 }, 

 5

 ProgramData { 

 6

 /// Slot that the program was last modified. 

 7

 slot : u64 , 

 8

 /// Address of the Program's upgrade authority. 

 9

 upgrade_authority_address : Option < Pubkey >, 

 10

 // The raw program data follows this serialized structure in the 

 11

 // account's data. 

 12

 }, 

```

```

 , // The raw program data follows this serialized structure in the // account's data.},"> 

 Eventually, the 
```
executable
```
 flag will be removed entirely as proposed in SIMD-0162 . The reasoning is simple: an accountâs owner and its content are sufficient to determine if itâs a valid program â the 
```
executable
```
 flag is redundant.

 This change is also a hard requirement for supporting the new loader-v4 . Unlike the upgradeable loader, which relies on a separate 
```
ProgramData
```
 proxy account, loader-v4 stores all program data directly in the program account itself.

 As a result, it becomes impossible to modify the accountâs size after deployment, or to migrate from the upgradeable loader to loader-v4 â without hitting the 
```
 ExecutableLamportChange 
```
 restriction.

### Fix 2: reject program accounts 

 To avoid this footgun, letâs explicitly skip any executable account:

```

```
 1

 pub fn can_transfer_lamports ( account : & AccountInfo , lamports : u64 ) -> Result < bool > { 

 2

 fn is_program ( account : & AccountInfo ) -> bool { 

 3

 account . executable 

 4

 } 

 5

 let rent = Rent :: get ()?; 

 6

 let balance_after = account . lamports () + lamports ; 

 7

 Ok ( account . is_writable 

 8

 && rent . is_exempt ( balance_after , account . data_len ()) 

 9

 && ! is_program ( account )) 

 10

 } 

```

```

 Result { fn is_program(account: &AccountInfo) -> bool { account.executable } let rent = Rent::get()?; let balance_after = account.lamports() + lamports; Ok(account.is_writable && rent.is_exempt(balance_after, account.data_len()) && !is_program(account))}"> 

 Now weâre safeâ¦right?

## Bug 3: the write-demotion trap 

 On Solana, accounts passed as writable in a transaction can be silently downgraded to read-only . This behavior occurs during message sanitization â even before your program runs.

 Letâs walk through the logic for legacy messages 1 :

```

```
 1

 // https://github.com/anza-xyz/solana-sdk/blob/master/message/src/sanitized.rs#L39-L55 

 2

 impl LegacyMessage < '_ > { 

 3

 pub fn new ( message : legacy :: Message , reserved_account_keys : & HashSet < Pubkey >) -> Self { 

 4

 let is_writable_account_cache = message 

 5

 . account_keys 

 6

 . iter () 

 7

 . enumerate () 

 8

 . map (|( i , _key )| { 

 9

 message . is_writable_index ( i ) 

 10

 && ! reserved_account_keys . contains (& message . account_keys [ i ]) 

 11

 && ! message . demote_program_id ( i ) 

 12

 }) 

 13

 . collect ::< Vec < _ >>(); 

 14

 Self { 

 15

 message : Cow :: Owned ( message ), 

 16

 is_writable_account_cache , 

 17

 } 

 18

 } 

 19

 } 

 20

 21

 // https://github.com/anza-xyz/solana-sdk/blob/master/message/src/legacy.rs#L642-L644 

 22

 pub fn demote_program_id (& self , i : usize ) -> bool { 

 23

 self . is_key_called_as_program ( i ) && ! self . is_upgradeable_loader_present () 

 24

 } 

```

```

 { pub fn new(message: legacy::Message, reserved_account_keys: &HashSet ) -> Self { let is_writable_account_cache = message .account_keys .iter() .enumerate() .map(|(i, _key)| { message.is_writable_index(i) && !reserved_account_keys.contains(&message.account_keys[i]) && !message.demote_program_id(i) }) .collect:: >(); Self { message: Cow::Owned(message), is_writable_account_cache, } }}// https://github.com/anza-xyz/solana-sdk/blob/master/message/src/legacy.rs#L642-L644pub fn demote_program_id(&self, i: usize) -> bool { self.is_key_called_as_program(i) && !self.is_upgradeable_loader_present()}"> 

 As you can see, there are two main causes of write-demotion:

- The account appears in the reserved account list .

- The account is invoked as a program without the upgradeable loader being present in the transaction.

 The second case is generally covered by the 
```
executable
```
 check implemented previously.

 The first case, however, is far more dangerous â it can silently break your program logic without any obvious cause. Letâs dig deeper into that.

### The reserved account list 

 The Solana runtime maintains a reserved account list , which includes addresses with special semantics â such as built-in programs, precompiles, and sysvars.

 These accounts may initially behave like normal accounts. However, once they become reserved after a feature gate is activated , the runtime will automatically demote them to read-only , even if the transaction marked them as writable:

```

```
 1

 // https://github.com/anza-xyz/agave/blob/0e6d9bf8c81cd94dfdedb500af4ac17328cf7a43/runtime/src/bank.rs#L6469-L6474 

 2

 // Update active set of reserved account keys which are not allowed to be write locked 

 3

 self . reserved_account_keys = { 

 4

 let mut reserved_keys = ReservedAccountKeys :: clone (& self . reserved_account_keys ); 

 5

 reserved_keys . update_active_set (& self . feature_set ); 

 6

 Arc :: new ( reserved_keys ) 

 7

 }; 

```

```

### Consequences: silent failures and bricked programs 

 This behavior is especially dangerous when you constrain a program to be writable. For example, with Anchor, itâs pretty common to use the 
```
 #[ account ( mut )] 
```
 constraint:

```

```
 1

 #[ derive ( Accounts )] 

 2

 pub struct ChangeKing < 'info > { 

 3

 #[ account ( mut )] 

 4

 pub throne : Account < 'info , Throne >, 

 5

 6

 #[ account ( mut , constraint = old_king . key () == throne . king )] 

 7

 pub old_king : AccountInfo < 'info >, 

 8

 9

 #[ account ( mut )] 

 10

 pub new_king : AccountInfo < 'info >, 

 11

 12

 #[ account ( mut )] 

 13

 pub payer : Signer < 'info >, 

 14

 } 

```

```

 { #[account(mut)] pub throne: Account , #[account(mut, constraint = old_king.key() == throne.king)] pub old_king: AccountInfo , #[account(mut)] pub new_king: AccountInfo , #[account(mut)] pub payer: Signer ,}"> 

 This works fine â until one day, 
```
old_king
```
 is silently demoted. Suddenly, the 
```
 #[ account ( mut )] 
```
 constraint fails, and your program is bricked. Even though youâre passing a writable account in the transaction, the runtime has made a unilateral decision to override that.

### Real-world example: write-demotion with 
```
secp256r1_program
```

 Hereâs a concrete example of the write-demotion trap playing out on mainnet â involving 
```
 secp256r1_program 
```
, a precompiled program gated behind a feature flag:

```

```
 ReservedAccount :: new_pending ( 

 secp256r1_program :: id (), 

 feature_set :: enable_secp256r1_precompile :: id (), 

 ) 

```

```

 Before the 
```
enable_secp256r1_precompile
```
 feature is activated, this account behaves like any ordinary one. You can assign 
```
 secp256r1_program :: id () 
```
 as the king in a contract.

 But once the feature is flipped on, the runtime silently marks it as read-only, blocking any future writes. As a result, 
```
 secp256r1_program :: id () 
```
 becomes the eternal king, and no one can dethrone it.

### Fix 3: preventing write-demotion pitfalls 

 Alright, letâs try to fix yet another edge case â and hopefully close the book on it.

### Attempt 1: block known reserved accounts 

 One naive solution is to reject any known reserved account, for example:

```

```
 1

 pub fn change_king ( ctx : Context < ChangeKing >, bid_amount : u64 ) -> Result <()> { 

 2

 assert! ( ctx . accounts . new_king . key () != secp256r1_program :: id ()); 

```

```

 , bid_amount: u64) -> Result { assert!(ctx.accounts.new_king.key() != secp256r1_program::id());"> 

 This works in the short term, but doesnât scale â you canât predict all future additions to the 
```
 ReservedAccount 
```
 list. The moment a new reserved account is introduced, your program becomes vulnerable again.

### Attempt 2: use a PDA vault 

 A more future-proof fix is to avoid transferring lamports to arbitrary accounts altogether.

 A clean approach would be to store the refund lamports in a PDA vault owned by your program. This prevents your logic from depending on accounts you donât have complete control over, and sidesteps any risk of write-demotion or future account restrictions.

## Final thoughts 

 Transferring lamports on Solana is not always straightforward and carries potential risks. Account constraints alone are insufficient to ensure safety, especially when dealing with runtime-specific edge cases.

 We can safely transfer lamports to an account under the following conditions:

- Itâs not executable.

- Its balance, after the transfer, remains rent-exempt.

- Itâs not a reserved account.

 This issue is not purely theoretical; it has impacted real-world programs. One significant case was recently reported to Jito via the bug bounty, which could have resulted in incorrect tip payments.

## Footnotes 

- 
 The same rules apply to MessageV0 , but legacy is simpler to follow. â©

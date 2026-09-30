# [H] OtterSec: Solana: an auditor’s introduction

## Summary
Severity: High
Published: Mon, 14 Mar 2022
Source: https://osec.io/blog/solana-security-intro/
Type: security-research

## Details
## Solana: an auditorâs introduction

 OtterSec Mar 14, 2022 #solana #tutorial A security-focused introduction to Solana, exploring the underlying runtime environment, security boundaries, and implications. An important resource for all developers who want to write more secure code.

## Introduction 

 This blog post is meant as a security-focused introduction to Solana. We explore how exactly Solanaâs runtime operates, what degree of control an attacker has, and any relevant security boundaries. That being said, we believe this is an important resource for all developers. With vulnerabilities putting millions in assets at risk, understanding what happens under the hood, even in passing, is crucial to writing safer code.

 Tip (Further reading) We would recommend also checking out Neodymeâs Security Workshop . This presents a good introduction to many different Solana vulnerability classes and is good for diving right in. In contrast, this blog post aims to start from fundamentals, presenting an overview of the Solana execution model from a security researcherâs perspective. With a strong understanding of how Solana contracts are executed, we believe that an astute researcher should be able to independently find such vulnerability classes â and more.

## Execution model 

 Understanding is crucial to finding vulnerabilities. When approaching a new contract, you should strive for a deep understanding of the contract, its various interactions, and any implicit assumptions.

 Hence, the first step is to understand how Solana programs even work. The Solana documentation on the programming model is another good resource.

 Solana programs are eBPF ELF files which are then loaded by an onchain program, the BPF loader . The ELF data is stored as part of an account onchain. An account can be thought of as a file, where the name of the account is the pubkey . Accounts in Solana are referenced by their pubkey. This relationship between pubkeys and accounts is a one-to-one mapping. Like files, accounts can have both data â arbitrary raw bytes â and additional metadata such as writable or executable that we will cover later. For more information on accounts, see the documentation .

 At a high level, interactions with onchain programs happen in the form of a program invocation. A Solana invocation specifies the following information:

- The program to call.

- A list of accounts.

- A list of bytes, the instruction data.

 Note how this execution model has no conception of methods . While naturally it might be useful to have different methods to call to perform different functions, this is not implemented at the execution level. Instead, this is done by parsing and interpreting the instruction data, for example, with an enum.

 The memory map is predefined and is as follows:

- Program code starts at 
```
0x100000000
```
.

- Stack data starts at 
```
0x200000000
```
.

- Heap data starts at 
```
0x300000000
```
.

- Program input parameters start at 
```
0x400000000
```
.

 Note Because most Solana programs are written in Rust, memory corruption is not a very common issue. Hence, we wonât be diving further into memory layout or other lower-level details.

 BPF programs define a common entrypoint:

```

```
 #[ no_mangle ] 

 pub unsafe extern "C" fn entrypoint ( input : * mut u8 ) -> u64 ; 

```

```

 u64;"> 

 This method will be called with a binary blob representing the serialized instruction and account data. Solana also provides utility functions to deserialize this data :

 entrypoint.rs 
```

```
 146

 pub unsafe fn deserialize < 'a >( input : * mut u8 ) -> (& 'a Pubkey , Vec < AccountInfo < 'a >>, & 'a [ u8 ]) { 

 147

 let mut offset : usize = 0 ; 

 148

 149

 // Number of accounts present 

 150

 151

 #[ allow ( clippy :: cast_ptr_alignment )] 

 152

 let num_accounts = *( input . add ( offset ) as * const u64 ) as usize ; 

 153

 offset += size_of ::< u64 >(); 

```

```

 (input: *mut u8) -> (&'a Pubkey, Vec >, &'a [u8]) { let mut offset: usize = 0; // Number of accounts present #[allow(clippy::cast_ptr_alignment)] let num_accounts = *(input.add(offset) as *const u64) as usize; offset += size_of:: ();"> 

 Note that this binary blob is not attacker-controlled . Instead, this data is serialized by another program called the BPF Loader , which is part of the Solana runtime:

 entrypoint.rs 
```

```
 /// Deserialize the input arguments 

 /// 

 /// The integer arithmetic in this method is safe when called on a buffer that was 

 /// serialized by runtime. Use with buffers serialized otherwise is unsupported and 

 /// done at one's own risk. 

```

```

 That being said, an attacker has a very large degree of control over this data. Letâs take a closer look at what exactly this data is.

 Recall the return signature of the 
```
 deserialize () 
```
 function:

```

```
 (& 'a Pubkey , Vec < AccountInfo < 'a >>, & 'a [ u8 ]) 

```

```

 >, &'a [u8])"> 

 The first part of the tuple represents the id of the running program. This is often used to check for proper ownership of accounts. For example, itâs generally only safe to operate on accounts that you own to ensure data integrity.

 The second part of the tuple is a list of account information:

 account_info.rs 
```

```
 1

 pub struct AccountInfo < 'a > { 

 2

 pub key : & 'a Pubkey , 

 3

 pub is_signer : bool , 

 4

 pub is_writable : bool , 

 5

 pub lamports : Rc < RefCell <& 'a mut u64 >>, 

 6

 pub data : Rc < RefCell <& 'a mut [ u8 ]>>, 

 7

 pub owner : & 'a Pubkey , 

 8

 pub executable : bool , 

 9

 pub rent_epoch : Epoch , 

 10

 } 

```

```

 { pub key: &'a Pubkey, pub is_signer: bool, pub is_writable: bool, pub lamports: Rc >, pub data: Rc >, pub owner: &'a Pubkey, pub executable: bool, pub rent_epoch: Epoch,}"> 

 This is the metadata associated with any given account. In other words, this represents all of the information that a Solana onchain program can know about an account. Some of the more important fields include:

- 
```
 key 
```
: The pubkey corresponding to this account.

- 
```
 is_signer 
```
: Whether there is a signature for this account, often used to allow privileged operations. See the docs .

- 
```
 is_writable 
```
: Whether the account can be modified, both with respect to lamports and account data.

- 
```
 lamports 
```
: A lamport is 0.000000001 SOL. Accounts have an associated amount of lamports.

 While which accounts to pass in is entirely attacker-controlled, the metadata associated with the account is not. For example, you can only specify an account as 
```
 is_signer 
```
 if you can generate a valid signature for it. Account data is also only modifiable by the account owner.

 Instruction data is a list of bytes and is entirely attacker-controlled.

 To summarize, we are able to call the 
```
 entrypoint 
```
 of any program with:

- Any accounts we choose.

- Any instruction data.

 You might already see how type confusion is 1 a huge issue on Solana. Because there is no execution-level typing of accounts, itâs very easy for a malicious user to pass in an account of the wrong type. Some solutions to implementing type information include hardcoding the pubkey of the account, storing a type tag, or both.

## Onchain programs 

 Solana also provides a number of native programs. An important thing to remember is that these native programs operate at a less privileged level than the execution model. In other words, any restrictions imposed by the execution model, such as not being able to write to readonly accounts, apply to the native programs as well.

 A full list of programs can be found here .

 The primary native program youâll likely interact with is the System Program:

```

```
 11111111111111111111111111111111 

```

```

 These instructions are processed in system_instruction_processor.rs :

 system_instruction_processor.rs 
```

```
 1

 match instruction { 

 2

 SystemInstruction :: CreateAccount { 

 3

 lamports , 

 4

 space , 

 5

 owner , 

 6

 } => { 

```

```

 {"> 

 A full list of the available instructions can be found by reading the source.

 To demonstrate some of the previous concepts, we will go over two instructions, 
```
 CreateAccount 
```
 and 
```
 Transfer 
```
.

```
 CreateAccount 
```
 requires the lamports, space, and owner to initialize the account with:

 system_instruction.rs 
```

```
 1

 pub fn create_account ( 

 2

 from_pubkey : & Pubkey , 

 3

 to_pubkey : & Pubkey , 

 4

 lamports : u64 , 

 5

 space : u64 , 

 6

 owner : & Pubkey , 

 7

 ) -> Instruction { 

 8

 let account_metas = vec! [ 

 9

 AccountMeta :: new (* from_pubkey , true ), 

 10

 AccountMeta :: new (* to_pubkey , true ), 

 11

 ]; 

 12

 Instruction :: new_with_bincode ( 

 13

 system_program :: id (), 

 14

 & SystemInstruction :: CreateAccount { 

 15

 lamports , 

 16

 space , 

 17

 owner : * owner , 

 18

 }, 

 19

 account_metas , 

 20

 ) 

 21

 } 

```

```

 Instruction { let account_metas = vec![ AccountMeta::new(*from_pubkey, true), AccountMeta::new(*to_pubkey, true), ]; Instruction::new_with_bincode( system_program::id(), &SystemInstruction::CreateAccount { lamports, space, owner: *owner, }, account_metas, )}"> 

 Both the from and to pubkeys are specified as signers (the boolean passed into 
```
 AccountMeta 
```
). This means that we need to have a valid signature for both:

```

```
 AccountMeta :: new (* from_pubkey , /*is_signer=*/ true ), 

 AccountMeta :: new (* to_pubkey , true ), 

```

```

 This is because the 
```
 lamports 
```
 used to create the account will come from the 
```
 from_account 
```
, thus lowering the balance of that account and requiring a signature.

 Internally, 
```
 CreateAccount 
```
 will call into 
```
 allocate_and_assign () 
```
, which allocates space for the account and assigns ownership:

 system_instruction_processor.rs 
```

```
 allocate ( invoke_context , signers , to_account , to_address , space )?; 

 assign ( invoke_context , signers , to_account , to_address , owner ) 

```

```

 Note You can also do these steps separately with the 
```
 Assign 
```
 and 
```
 Allocate 
```
 instructions:

 system_instruction.rs 
```

```
 Assign { 

 owner : Pubkey , 

 }, 

 ... 

 Allocate { 

 space : u64 , 

 }, 

```

```

 In contrast, consider the instruction for 
```
 Transfer 
```
:

 system_instruction.rs 
```

```
 1

 pub fn transfer ( from_pubkey : & Pubkey , to_pubkey : & Pubkey , lamports : u64 ) -> Instruction { 

 2

 let account_metas = vec! [ 

 3

 AccountMeta :: new (* from_pubkey , true ), 

 4

 AccountMeta :: new (* to_pubkey , false ), 

 5

 ]; 

 6

 Instruction :: new_with_bincode ( 

 7

 system_program :: id (), 

 8

 & SystemInstruction :: Transfer { lamports }, 

 9

 account_metas , 

 10

 ) 

 11

 } 

```

```

 Instruction { let account_metas = vec![ AccountMeta::new(*from_pubkey, true), AccountMeta::new(*to_pubkey, false), ]; Instruction::new_with_bincode( system_program::id(), &SystemInstruction::Transfer { lamports }, account_metas, )}"> 

 Note how only 
```
 from_pubkey 
```
 needs a signature. Intuitively this makes sense because we donât need permission to transfer funds into an account (at least in Solanaâs permission model).

 The 
```
 transfer () 
```
 implementation in 
```
system_instruction_processor.rs
```
 indeed checks for the signature:

 system_instruction_processor.rs 
```

```
 1

 if ! instruction_context 

 2

 . is_signer ( instruction_context . get_number_of_program_accounts () + from_account_index )? 

 3

 { 

 4

 ic_msg! ( 

 5

 invoke_context , 

 6

 "Transfer: `from` account {} must sign" , 

 7

 instruction_context . get_instruction_account_key ( 

 8

 invoke_context . transaction_context , 

 9

 from_account_index 

 10

 )?, 

 11

 ); 

 12

 return Err ( InstructionError :: MissingRequiredSignature ); 

 13

 } 

```

```

 Note that because the System Program runs at a higher level than the execution runtime, the System Program can only transfer funds out of accounts that it owns. In other words, 
```
 transfer () 
```
 does not work on arbitrary Solana accounts, even if you can generate a valid signature for it. By default, all user pubkeys are owned by the System Program:

 Terminal window 
```

```
 $ solana account 6ZRCB7AAqGre6c72PRz3MHLC73VMYvJ8bi9KHf1HFpNk 

 Public Key: 6ZRCB7AAqGre6c72PRz3MHLC73VMYvJ8bi9KHf1HFpNk 

 Balance: 1152042.467511623 SOL 

 Owner: 11111111111111111111111111111111 

 Executable: false 

 Rent Epoch: 288 

```

```

 An example of an account which is not owned by the System Program is a token account, which stores how many tokens a user has:

 Terminal window 
```

```
 $ solana account 4W4dtYi4rXTegfR6byhmP17VJo4MaUWWCt3zzLnZVKGZ 

 Public Key: 4W4dtYi4rXTegfR6byhmP17VJo4MaUWWCt3zzLnZVKGZ 

 Balance: 0.00203928 SOL 

 Owner: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA 

 Executable: false 

 Rent Epoch: 288 

 Length: 165 (0xa5) bytes 

 0000: 06 83 10 86 1a 98 32 7d 05 50 57 4d 84 41 8a a6 ......2}.PWM.A.. 

 0010: e1 0c 33 52 dd aa 7f d7 f5 81 52 cc ee b2 38 87 ..3R......R...8. 

 0020: 52 98 60 10 57 37 39 df 4b 58 ba 50 e3 9c f3 f3 R.`.W79.KX.P.... 

 0030: 35 b8 9c c7 d1 cb 1d 32 b5 de 04 ef a0 68 c9 39 5......2.....h.9 

 0040: 40 0d 03 00 00 00 00 00 00 00 00 00 00 00 00 00 @............... 

 0050: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................ 

 0060: 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 ................ 

 0070: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................ 

 0080: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................ 

 0090: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ................ 

 00a0: 00 00 00 00 00 

```

```

 This is an example of a program derived address .

 Note An astute reader might also notice that the original pubkey is embedded in the token account data starting at position 
```
0x20
```
. Intuitively, the token account must store its owner somewhere, and this is often done by storing the owner pubkey in the account data.

## Closing thoughts 

 There are many intricacies to Solanaâs programming model which we will perhaps explore in future blog posts. For example, how do user accounts created with 
```
 solana-keygen 
```
 work? What exactly is the account validation scheme?

 While it may be tempting to treat Solana as a black box, the code itself is all open source. We believe a crucial part of security is building a deep understanding of the underlying system. This requires digging into the Solana runtime. We hope this and future posts present an interesting perspective on the Solana runtime.

 Please reach out if you found this useful or have any additional thoughts to share.

## Footnotes 

- 
 Or was, before Anchor. â©

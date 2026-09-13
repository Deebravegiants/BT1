# [H] OtterSec: Reverse engineering Solana with Binary Ninja

## Summary
Severity: High
Published: Sat, 27 Aug 2022
Source: https://osec.io/blog/reverse-engineering-solana/
Type: security-research

## Details
## Reverse engineering Solana with Binary Ninja

 Harrison Green Aug 27, 2022 #solana An introduction to our open-source Binary Ninja plugin for blackbox Solana program analysis along with an executive reference to the Solana runtime.

## Introduction 

 We are excited to announce the release of our open-source Binary Ninja plugin for Solana ! We have been hard at work developing this tool internally to aid our efforts in blackbox Solana program analysis. While it is still in development, it is now mature enough to be useful (and usable) and we have decided to release it to the larger security community. You can find it on GitHub here: https://github.com/otter-sec/bn-ebpf-solana . If you find bugs in our plugin or want to add improvements, please open an issue or submit a PR!

 In this blog post, we will provide some background on the Solana runtime and describe the various components of our plugin. In subsequent blog posts, we will dive into case studies of using this tool to decompile and analyze closed-source Solana programs.

## A primer on the Solana runtime 

## Solana programs 

 Solana programs are written in Rust or C (currently) and compiled to a Solana-flavored eBPF ELF format. These ELF files are stored in data accounts on-chain and contain all the information required to actually run the programs. Oftentimes, the compiler will throw out irrelevant, human-only information like variable names and function names.

## Solana virtual machine 

 While eBPF was originally designed for use in the Linux kernel, Solana has adapted a slightly modified version for use on the blockchain. A Solana program runs in a completely isolated environment except for two interfaces:

- The 
```
input
```
 memory segment, used for passing information about the initial arguments to a program (accounts, instruction info, transaction context, etc.).

- A set of 
```
syscalls
```
 which allow Solana programs to interact with the runtime through a well-defined API.

## Memory model 

 Memory segments are relocated to specific regions in the Solana memory model:

- 
```
0x100000000
```
: Text â contains code and read-only data from the ELF.

- 
```
0x200000000
```
: Stack â dedicated space for stack data.

- 
```
0x300000000
```
: Heap â dedicated space for heap storage.

- 
```
0x400000000
```
: Input â contains serialized input data. This is populated by the runtime every time a program runs.

## Transactions and instructions 

 In Solana, you interact with programs by issuing a Transaction. Every Transaction consists of one or more Instructions. Conceptually, each Instruction is responsible for invoking âone functionâ on a particular program:

 Note This doesnât necessarily have to be the case, but this is how most Solana programs are designed.

 Each 
```
Instruction
```
 contains the following attributes:

- 
```
program_id
```
: The address of the program we want to invoke.

- 
```
accounts
```
: A list of accounts we will use during execution. 1 

- 
```
data
```
: Arbitrary data that is passed to the program.

 Unlike some other blockchain architectures, programs in Solana have just one entrypoint. Programs that want to implement multiple âfunctionsâ need to do so in user-space. Typically, this is handled by a high-level framework such as Anchor :

 At the binary level, the 
```
entrypoint
```
 is implemented by defining a symbol in the ELF with the name âentrypointâ that points to the first function to run. For example, in C, this is as simple as defining the following function:

```

```
 extern uint64_t entrypoint ( const uint8_t * input ) { 

 // do things 

 } 

```

```

 In order to process an instruction, the runtime does the following steps (in brief):

- Look up the 
```
program_id
```
 account.

- Look up the loader for the program. 2 

- Parse the ELF file and construct an instance of the VM (the runtime may do some optimizations such as JITing the program).

- Serialize the 
```
accounts
```
 and transaction context into the 
```
input
```
 segment of the VM.

- Invoke the 
```
entrypoint
```
 function in the program with the Instruction 
```
data
```
 as an argument.
 
- â¦ program logic runs here â¦

- Deserialize the 
```
input
```
 segment, validate the changes, and commit the results back to the global state.

## Cross-program invocation 

 Solana programs can also invoke other programs directly. This is called cross-program invocation (CPI). In Solana, this is achieved through syscalls (
```
 sol_invoke_signed_c 
```
 or 
```
 sol_invoke_signed_rust 
```
) which differ only in the ABI.

 Using these syscalls, a program can issue instructions that execute on other programs. Importantly, any accounts used in these nested instructions must also be provided in the initial instruction.

 In the following diagram, 
```
MyProgram
```
 performs two cross-program invocations on some mock 
```
token-mgr
```
 program which has some 
```
Burn
```
 and 
```
Mint
```
 actions. The notation 
```
[Instr()]
```
 represents a serialized enum:

 Note that the 
```
token-mgr
```
 program account must be listed in the original instruction in order to perform a CPI on it. Additionally, note that the two cross-program calls to 
```
token-mgr
```
 invoke the same entrypoint. The choice of action to take is determined by looking at the value in the provided 
```
data
```
.

 When a Solana program invokes one of these syscalls, the current VM is paused and the runtime goes through the same steps as above to load the target program into a new VM and execute it. Once the cross-program invocation completes, the original VM resumes execution.

 Programs can set and get return data via the 
```
 sol_set_return_data 
```
 and 
```
 sol_get_return_data 
```
 syscalls, allowing for some information to be passed between these calls.

 Note Currently, there are some bounds on CPI. Specifically, the depth (number of nested calls) is limited to 4 and reentrancy is mostly prohibited.

## Solana program analysis 

## What information do we have? 

 As auditors, we always have access to our customersâ source code. This access has a lot of benefits when it comes to understanding how a piece of code works:

- There are symbol names (functions, variables, â¦).

- There are full structure definitions.

- There are comments (and hopefully documentation).

- We can easily recompile and test things.

 While most protocols built on Solana release their code as open source, some do not. Therefore, without exclusive auditor access to the source code, one may be left exploring other options. Additionally, an attacker is definitely not going to publish the source code for their malicious programs, so what other information can we use?

## Transaction history 

 One particularly useful technique is to look at previous instructions executed on a particular program in the explorer . When an instruction is executed, lots of useful information is stored:

- Logs : Solana programs can write log strings via the 
```
sol_log_*
```
 syscalls. Oftentimes, programs will log the name of the instruction being executed, which lets you easily pick apart instruction formats.

- CPI results : Every nested cross-program invocation will be stored as part of the instruction result. These details include the full 
```
Instruction
```
 object for every call, which lets us see exactly which programs were invoked and with what set of addresses and data. Many DeFi protocols make calls to token management programs such as 
```
spl-token
```
, which lets us easily see how money is being transferred.

## Diving deeper 

 While these techniques are useful for analyzing the effect a particular instruction had (i.e. what did it call? , what did it do? ), we are so far unable to understand exactly how the program operates: What decisions does it make? What is it capable of doing? How was it designed?

 To get into those more complex details, we need to actually analyze the compiled eBPF program. While tooling for traditional native binaries is quite advanced, there are not many existing tools for Solana binary analysis. So we decided to develop our own tool for Solana program analysisâ¦

## bn-ebpf-solana 

 bn-ebpf-solana is an open-source plugin for Binary Ninja that supports Solana-flavored eBPF. It is still a work in progress; there are several features we are planning to add that will make blackbox Solana program analysis easier. However, in its current stage it has proved useful for our own internal analyses and we have decided to make it open source so it can be useful for other people as well!

 The plugin consists of two parts:

- An architecture plugin which supports the Solana flavor of eBPF.

- A custom BinaryView implementation which understands the Solana ELF format and Solana-specific relocations.

 Currently, the following features are supported:

## Instruction lifting 

 LLIL lifting is implemented for all eBPF instructions, which allows Binary Ninja to perform local static analysis and generate concise decompilation (left: CFG disassembly view; right: linear HLIL view):

## Accurate memory maps 

 ELF sections are relocated into the 
```
0x100000000
```
 range as implemented by the core runtime code. Additional segments are created at 
```
0x{2/3/4}00000000
```
 for the 
```
stack
```
, 
```
heap
```
 and 
```
input
```
 segments:

## Solana ELF relocations 

 We apply the Solana-specific ELF relocations as implemented by the core runtime.

## Syscall function signatures 

 We identify Solana syscalls, convert them to calls and apply the correct function signatures.

 In this example, the 
```
 sol_panic_ 
```
 signature is applied automatically as soon as you open the eBPF 
```
.so
```
 file:

## Solana SDK types 

 We autopopulate the analysis view with Solana SDK types (C is fully supported, Rust is still a work-in-progress). These types allow for full structure recovery of Solana objects used at runtime:

 Compare this code with the corresponding source code (from the 
```
solfire
```
 challenge from PicoCTF 2022):

 solfire.c 
```

```
 1

 sol_assert ( payee -> is_signer ); 

 2

 sol_assert ( params -> data_len - 4 >= sizeof(* args )); 

 3

 4

 args = ( withdraw_args *) ( params -> data + 4 ); 

 5

 sol_assert ( args -> idx <= MARKET_CNT ); 

 6

 sol_assert ( args -> amt != 0 ); 

 7

 8

 uint8_t seed [] = { 'v' , 'a' , 'u' , 'l' , 't' , 'x' }; 

 9

 seed [ 5 ] = args -> bump ; 

 10

 11

 const SolSignerSeed seeds [] = {{ seed , SOL_ARRAY_SIZE ( seed )}}; 

 12

 const SolSignerSeeds signers_seeds [] = {{ seeds , SOL_ARRAY_SIZE ( seeds )}}; 

 13

 14

 SolAccountMeta arguments [] = { 

 15

 { vault -> key , true , true }, 

 16

 { payee -> key , true , false }, 

 17

 }; 

 18

 uint8_t data [ 4 + sizeof( transfer_amount_sys )]; 

 19

 sol_memset ( data , 0 , sizeof( data )); 

 20

 21

 *( uint16_t *) data = TRANSFER ; 

 22

 transfer_amount_sys * data_args = ( transfer_amount_sys *) ( data + 4 ); 

 23

 data_args -> lamports = args -> amt ; 

 24

 25

 const SolInstruction instruction = { system_program -> key , arguments , 

 26

 SOL_ARRAY_SIZE ( arguments ), data , 

 27

 SOL_ARRAY_SIZE ( data )}; 

 28

 sol_invoke_signed (& instruction , params -> ka , params -> ka_num , 

 29

 signers_seeds , SOL_ARRAY_SIZE ( signers_seeds )); 

 30

 31

 LendingData * ld_obj = ( LendingData *) ld_acct -> data ; 

 32

 Market * market = & ld_obj -> markets [ args -> idx ]; 

 33

 market -> liab += args -> amt ; 

 34

 sol_assert ( market -> liab <= market -> collat ); 

```

```

 is_signer);sol_assert(params->data_len - 4 >= sizeof(*args));args = (withdraw_args*) (params->data + 4);sol_assert(args->idx amt != 0);uint8_t seed[] = { 'v', 'a', 'u', 'l', 't', 'x' };seed[5] = args->bump;const SolSignerSeed seeds[] = {{seed, SOL_ARRAY_SIZE(seed)}};const SolSignerSeeds signers_seeds[] = {{seeds, SOL_ARRAY_SIZE(seeds)}};SolAccountMeta arguments[] = { {vault->key, true, true}, {payee->key, true, false},};uint8_t data[4 + sizeof(transfer_amount_sys)];sol_memset(data, 0, sizeof(data));*(uint16_t *)data = TRANSFER;transfer_amount_sys* data_args = (transfer_amount_sys*) (data + 4);data_args->lamports = args->amt;const SolInstruction instruction = {system_program->key, arguments, SOL_ARRAY_SIZE(arguments), data, SOL_ARRAY_SIZE(data)};sol_invoke_signed(&instruction, params->ka, params->ka_num, signers_seeds, SOL_ARRAY_SIZE(signers_seeds));LendingData* ld_obj = (LendingData*) ld_acct->data;Market* market = &ld_obj->markets[args->idx];market->liab += args->amt;sol_assert(market->liab collat);"> 

## Whatâs next? 

 Weâre planning to follow up this introductory blog post with a series of case studies of blackbox Solana program analysis using our Binary Ninja plugin. Stay tuned!

## Footnotes 

- 
 Solana requires us to predefine which accounts we will need to access during our instruction so the runtime can parallelize instructions that operate on disjoint sets. â© 

- 
 All user-written programs currently use a variant of the BPF loader, which is the one responsible for running BPF code. However, Solana is designed in a way where additional loaders may be available in the future. â©

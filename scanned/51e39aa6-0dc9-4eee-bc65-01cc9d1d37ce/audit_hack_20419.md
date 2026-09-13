# [H] OtterSec: Solidity compilers: memory safety

## Summary
Severity: High
Published: Fri, 28 Jul 2023
Source: https://osec.io/blog/solidity-compilers-memory-safety/
Type: security-research

## Details
## Solidity compilers: memory safety

 Robert Chen Jul 28, 2023 #solidity #compiler An exploration into the Solidity compilation pipeline, optimization assumptions, and how it all relates back to memory-safe assembly.

## Introduction 

 What does 
```
memory-safe
```
 actually mean? What guarantees does Solidity expose when youâre dealing with inline assembly? The documentation presents some requirements , but is production code that violates these requirements necessarily unsafe?

 In this blog post, we present a high-level overview of the Solidity compiler. Weâll also dive into the optimization pipeline, language lawyering, and present an argument for what memory safety actually means.

## Compiler pipeline 

 For brevityâs sake, weâll only cover the YUL IR Solidity compilation pipeline released in v0.8.13 . Compilation happens in two main steps :

- Solidity to YUL IR

- YUL IR to EVM opcodes

 CompilerStack.cpp 
```

```
 684

 if ( m_viaIR || m_generateIR || m_generateEwasm ) 

 685

 generateIR (* contract ); 

 686

 if ( m_generateEvmBytecode ) 

 687

 { 

 688

 if ( m_viaIR ) 

 689

 generateEVMFromIR (* contract ); 

 690

 else 

 691

 compileContract (* contract , otherCompilers ); 

 692

 } 

```

```

 Each step applies its own set of optimizations. The entrypoints are located at 
```
 YulStack :: optimize 
```
 and 
```
 Assembly :: optimize 
```
 .

 In total, there are four steps:

- Solidity to YUL IR

- Optimization of YUL IR

- YUL IR to EVM opcodes

- Optimization of EVM opcodes

 As mentioned in the v0.8.13 release post, the YUL optimizer is able to perform much more complex optimizations. Compared to Solidity, YUL contains detailed semantic information and is simpler for optimization passes to reason about than opcodes.

 The performance of the new pipeline is not yet always superior to the old one, but it can do much higher-level optimization across functions, so please try it out and give us feedback!

 Importantly, each step happens in isolation and retains no information about the previous stage.

 The optimizer cannot change the behavior of the generated IR. This means we donât need to worry about potentially tricky optimizations such as reordering of functions, removal of unused assigns, or moving stack variables to memory.

 When it comes to safety, we need only to consider the IR generation. But what exactly are the guarantees here?

## Guarantees 

 The Solidity memory layout exists only at the time of YUL IR generation. The YUL optimizer and later steps have no information about this layout .

 What if the optimizer wants to use memory for optimization passes? How does it know what slots are used by the IR generator?

 Introducing 
```
 memoryguard 
```
. If youâve ever looked at the output of 
```
 solc --ir 
```
, this call may be familiar. Itâs used to initialize the free memory pointer:

```

```
 /// @src 0:26:371 "contract XXX {..." 

 mstore ( 64 , memoryguard ( 0x80 )) 

```

```

 From the documentation :

 The caller of 
```
let ptr := memoryguard(size)
```
 (where size has to be a literal number) promises that they only use memory in either the range 
```
[0, size)
```
 or the unbounded range starting at 
```
ptr
```
.

 For example, if the YUL optimizer needs 32 bytes of memory, it can have 
```
 memoryguard 
```
 return 
```
size + 32
```
. The optimizer gets a guaranteed region of memory which will not be touched!

 An example of this optimization in practice is the 
```
StackLimitEvader
```
 , which moves variables from the stack into memory. Incidentally, this is also currently the only optimization pass that relies on the semantic information communicated by 
```
 memoryguard 
```
.

 Tip (Removing the free memory pointer) The modular design between different compiler stages also means that weâre not tied down to any particular memory layout. Does it make sense to waste an entire memory word on the free memory pointer? Maybe not for some applications.

 Fear not, for we can remove this pointer entirely and call 
```
 memoryguard ( 0x60 ) 
```
 instead. The rest of the pipeline will still work.

## Memory safety 

 So what does memory safety mean?

 The Solidity documentation provides a set of constraints , not a definition:

 In particular, a memory-safe assembly block may only access the following memory ranges:

- Memory allocated by yourself using a mechanism like the allocate function described above.

- Memory allocated by Solidity, e.g. memory within the bounds of a memory array you reference.

- The scratch space between memory offset 0 and 64 mentioned above.

- Temporary memory that is located after the value of the free memory pointer at the beginning of the assembly block, i.e. memory that is âallocatedâ at the free memory pointer without updating the free memory pointer.

 Looking to the compiler, it appears the presence of memory-unsafe assembly removes the memory guard 1 :

 IRGenerator.cpp 
```

```
 1

 // bool creationInvolvesMemoryUnsafeAssembly = m_context.memoryUnsafeInlineAssemblySeen(); 

 2

 // t("memoryInitCreation", memoryInit(!creationInvolvesMemoryUnsafeAssembly)); 

 3

 4

 string IRGenerator :: memoryInit ( bool _useMemoryGuard ) 

 5

 { 

 6

 // This function should be called at the beginning of the EVM call frame 

 7

 // and thus can assume all memory to be zero, including the contents of 

 8

 // the "zero memory area" (the position CompilerUtils::zeroPointer points to). 

 9

 return 

 10

 Whiskers { 

 11

 _useMemoryGuard ? 

 12

 "mstore(<memPtr>, memoryguard(<freeMemoryStart>))" : 

 13

 "mstore(<memPtr>, <freeMemoryStart>)" 

 14

 } 

```

```

 , memoryguard( ))" : "mstore( , )" }"> 

```
 solc --ir 
```
 will now no longer have 
```
 memoryguard ( 0x80 ) 
```
 as expected:

```

```
 /// @src 0:26:371 "contract XXX {..." 

 mstore ( 64 , 128 ) 

```

```

 Semantically, the absence of 
```
 memoryguard 
```
 means that the IR generator is telling the optimizer that it cannot guarantee the 
```
 memoryguard 
```
 invariant:

 The caller of 
```
let ptr := memoryguard(size)
```
 (where size has to be a literal number) promises that they only use memory in either the range 
```
[0, size)
```
 or the unbounded range starting at 
```
ptr
```
.

 This makes sense. Without stricter guarantees by the programmer, memory-unsafe assembly can touch memory anywhere it wants. Because the optimizer no longer has this guarantee, it cannot use memory in any of its optimization passes.

## Undefined behavior 

 How strict is memory safety? When it comes to 
```
 memoryguard 
```
, only touching memory after 
```
0x80
```
 seems to matter. Is 
```
memory-safe
```
 annotated assembly that touches memory at 
```
[0x40, 0x7f]
```
 really safe?

 The Solidity documentation mentions undefined behavior three times:

- The existence of a dangling reference.

- Using 
```
verbatim
```
 improperly. 2 

- Violating the memory model with inline assembly marked as âmemory-safeâ.

 Why does this matter?

 Assumptions about the program code can enable powerful optimizations â thatâs why signed integer overflow is undefined . Strictly following the compiler model is critical. Undefined behavior materializes as tricky bugs years down the line .

 Going back to Solidity, the specification makes it unambiguously clear . Thou shalt not modify the zero slot .

 The zero slot is used as initial value for dynamic memory arrays and should never be written to (the free memory pointer points to 0x80 initially).

 Any code that touches the zero slot at 
```
0x60
```
 is very clearly violating the specification. Does this matter though? This is where the semantics between Solidity and YUL get tricky. Recall that the zero slot is a construction in Solidity .

 Even though thereâs no explicit guarantee that inline assembly will be emitted verbatim during generation:

- 
 It very clearly holds true today :

 IRGeneratorForStatements.cpp 
```

```
 2216

 bool IRGeneratorForStatements :: visit ( InlineAssembly const& _inlineAsm ) 

 2217

 { 

 2218

 setLocation ( _inlineAsm ); 

 2219

 if (* _inlineAsm . annotation (). hasMemoryEffects && ! _inlineAsm . annotation (). markedMemorySafe ) 

 2220

 m_context . setMemoryUnsafeInlineAssemblySeen (); 

 2221

 CopyTranslate bodyCopier { _inlineAsm . dialect (), m_context , _inlineAsm . annotation (). externalReferences }; 

 2222

 2223

 yul :: Statement modified = bodyCopier ( _inlineAsm . operations ()); 

```

```

- 
 It would require a pretty contrived compiler implementation to meaningfully modify assembly statements before optimization.

 As long as the invariants are upheld before and after the assembly block executes, the code is probably safe.

## Closing thoughts 

 In this blog post, we present an exploration of the Solidity compiler. This aims to serve as a useful reference for the inquisitive. Compilers are extremely complex with implicit and explicit assumptions. When in doubt, read the source code. So what exactly is memory safety?

 Itâs a promise between YUL generation and optimization.

## Footnotes 

- 
 As an interesting aside, 
```
 memoryguard 
```
 is an opaque function which prevents optimizations from reasoning about the free memory pointer. This leads to some rather counterintuitive behavior â 
```
memory-unsafe
```
 code can decrease gas consumption, especially in the YUL header. â© 

- 
 Unfortunately, the documentation only presents a ânon-exhaustive list of restrictionsâ on verbatim bytecode. In practice, it seems hard to guarantee behavior with opaque bytes. â©

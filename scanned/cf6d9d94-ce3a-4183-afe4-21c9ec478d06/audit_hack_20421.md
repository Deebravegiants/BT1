# [H] OtterSec: Rust, realloc, and references

## Summary
Severity: High
Published: Fri, 09 Dec 2022
Source: https://osec.io/blog/rust-realloc-and-references/
Type: security-research

## Details
## Rust, realloc, and references

 Ethan Wu Dec 9, 2022 #report #tutorial Rust is safeâ¦ right? Not if your dependencies are unsafeâ¦ A deep dive into a subtle Solana SDK bug, Rust internals, and how we found it all.

## Introduction 

 It all started with an audit of a program that used 
```
 realloc 
```
 on an account, without any bounds checks on the new size allowed. It seemed like the developers assumed that if the new size was too large, the 
```
 realloc 
```
 call (from 
```
 solana_program 
```
) would error out appropriately.

 But weâre not ones to just assume things around here, so letâs take a look at how 
```
 AccountInfo :: realloc 
```
 is implemented :

 account_info.rs 
```

```
 124

 pub fn realloc (& self , new_len : usize , zero_init : bool ) -> Result <(), ProgramError > { 

 125

 let orig_len = self . data_len (); 

 126

 127

 // realloc 

 128

 unsafe { 

 129

 // First set new length in the serialized data 

 130

 let ptr = self . try_borrow_mut_data ()?. as_mut_ptr (). offset (- 8 ) as * mut u64 ; 

 131

 * ptr = new_len as u64 ; 

 132

 133

 // Then set the new length in the local slice 

 134

 let ptr = & mut *((( self . data . as_ptr () as * const u64 ). offset ( 1 ) as u64 ) as * mut u64 ); 

 135

 * ptr = new_len as u64 ; 

 136

 } 

 137

 138

 // zero-init if requested 

 139

 if zero_init && new_len > orig_len { 

 140

 sol_memset ( 

 141

 & mut self . try_borrow_mut_data ()?[ orig_len ..], 

 142

 0 , 

 143

 new_len . saturating_sub ( orig_len ), 

 144

 ); 

 145

 } 

 146

 147

 Ok (()) 

 148

 } 

```

```

 Result { let orig_len = self.data_len(); // realloc unsafe { // First set new length in the serialized data let ptr = self.try_borrow_mut_data()?.as_mut_ptr().offset(-8) as *mut u64; *ptr = new_len as u64; // Then set the new length in the local slice let ptr = &mut *(((self.data.as_ptr() as *const u64).offset(1) as u64) as *mut u64); *ptr = new_len as u64; } // zero-init if requested if zero_init && new_len > orig_len { sol_memset( &mut self.try_borrow_mut_data()?[orig_len..], 0, new_len.saturating_sub(orig_len), ); } Ok(())}"> 

 Oh. Thereâs 
```
 unsafe 
```
. And no bounds check in sight. And pointer math. That doesnât look promisingâ¦

## Breaking down 
```
realloc
```

 Letâs pick apart this 
```
 unsafe 
```
 block, since thereâs a lot going on here:

```

```
 // First set new length in the serialized data 

 let ptr = self . try_borrow_mut_data ()?. as_mut_ptr (). offset (- 8 ) as * mut u64 ; 

 * ptr = new_len as u64 ; 

```

```

```
 try_borrow_mut_data 
```
 returns a mutable reference to the underlying buffer holding the data of the account. Normally in the course of contract execution, this comes from the serialized buffer passed into the contract by the BPF loader. So before we can understand the details here, letâs take a quick detourâ¦

## BPF loader ABI 

 Solana smart contracts have one job: interact with on-chain accounts. So whatâs the interface between the contract and the rest of the chain? To answer that, weâre going to take a look at 
```
 solana_program 
```
âs entrypoint code - the code thatâs added when you use the 
```
 entrypoint! 
```
 macro :

 entrypoint.rs 
```

```
 1

 #[ no_mangle ] 

 2

 pub unsafe extern "C" fn entrypoint ( input : * mut u8 ) -> u64 { 

 3

 let ( program_id , accounts , instruction_data ) = 

 4

 unsafe { $ crate :: entrypoint :: deserialize ( input ) }; 

 5

 match $ process_instruction (& program_id , & accounts , & instruction_data ) { 

 6

 Ok (()) => $ crate :: entrypoint :: SUCCESS , 

 7

 Err ( error ) => error . into (), 

 8

 } 

 9

 } 

```

```

 u64 { let (program_id, accounts, instruction_data) = unsafe { $crate::entrypoint::deserialize(input) }; match $process_instruction(&program_id, &accounts, &instruction_data) { Ok(()) => $crate::entrypoint::SUCCESS, Err(error) => error.into(), }}"> 

 What we see here is the contractâs real entrypoint - it takes a 
```
 u8 
```
 buffer in from the loader, and calls 
```
 solana_program :: entrypoint :: deserialize 
```
, which then parses out all the 
```
 AccountInfo 
```
s, instruction data, and the current running program ID. We can see how the data buffer is laid out :

 entrypoint.rs 
```

```
 1

 #[ allow ( clippy :: cast_ptr_alignment )] 

 2

 let data_len = *( input . add ( offset ) as * const u64 ) as usize ; 

 3

 offset += size_of ::< u64 >(); 

 4

 5

 let data = Rc :: new ( RefCell :: new ({ 

 6

 from_raw_parts_mut ( input . add ( offset ), data_len ) 

 7

 })); 

 8

 offset += data_len + MAX_PERMITTED_DATA_INCREASE ; 

 9

 offset += ( offset as * const u8 ). align_offset ( BPF_ALIGN_OF_U128 ); // padding 

```

```

 ();let data = Rc::new(RefCell::new({ from_raw_parts_mut(input.add(offset), data_len)}));offset += data_len + MAX_PERMITTED_DATA_INCREASE;offset += (offset as *const u8).align_offset(BPF_ALIGN_OF_U128); // padding"> 

 In English, we have the length of the data, as a 
```
 u64 
```
, followed immediately by the data, and an additional 
```
 MAX_PERMITTED_DATA_INCREASE 
```
 of reserve space (+ padding) after that. Using the length and data pointer, we construct a Rust slice reference ( 
```
 slice :: from_raw_parts_mut 
```
 ) - slices are how Rust represents a, well, slice (contiguous chunk) of memory - then wrap it up inside a 
```
 Rc < RefCell < T >> 
```
, giving us the unwieldy-looking type of 
```
 AccountInfo . data 
```
: 
```
 Rc < RefCell <& mut [ u8 ]>> 
```
.

 Now, whatâs the point of this complicated type? Thatâs because when the same account is passed in multiple times to a program, instead of duplicating the data for the account, the BPF loader simply refers back to the first instance of the account. On the Rust side, that corresponds to cloning the referenced account :

 entrypoint.rs 
```

```
 // Duplicate account, clone the original 

 accounts . push ( accounts [ dup_info as usize ]. clone ()); 

```

```

 Since 
```
 data 
```
 inside the 
```
 AccountInfo 
```
 is a 
```
 Rc < RefCell < T >> 
```
, where the 
```
 T 
```
 is a 
```
 & mut [ u8 ] 
```
 pointing at the actual data buffer, when we clone the 
```
 AccountInfo 
```
, we get a new reference 1 to the slice pointing at the same data buffer.

 And of course to uphold borrowing rules while having a shared pointer, we have interior mutability via 
```
 RefCell 
```
 to check the rules at runtime. 2 

 Changing the data of an account is done by simply writing to 
```
 AccountInfo :: data 
```
, which, as we just saw, is basically a pointer into the serialized buffer from the runtime; after the program exits, the loader reads the buffer back in to look at what the new state of the accounts should be.

 This is also where the runtime validity checks are imposed:

 pre_account.rs 
```

```
 1

 // Only the owner may change account data 

 2

 // and if the account is writable 

 3

 // and if the account is not executable 

 4

 if !( program_id == pre . owner () 

 5

 && is_writable // line coverage used to get branch coverage 

 6

 && ! pre . executable ()) 

 7

 && pre . data () != post . data () 

 8

 { 

 9

 if pre . executable () { 

 10

 return Err ( InstructionError :: ExecutableDataModified ); 

 11

 } else if is_writable { 

 12

 return Err ( InstructionError :: ExternalAccountDataModified ); 

 13

 } else { 

 14

 return Err ( InstructionError :: ReadonlyDataModified ); 

 15

 } 

 16

 } 

```

```

## Back to 
```
realloc
```

 As a reminder, this is what we were looking at before that detour:

```

```
 // First set new length in the serialized data 

 let ptr = self . try_borrow_mut_data ()?. as_mut_ptr (). offset (- 8 ) as * mut u64 ; 

 * ptr = new_len as u64 ; 

```

```

```
 try_borrow_mut_data 
```
 gives us the 
```
 & mut [ u8 ] 
```
 from the 
```
 Rc < RefCell <& mut [ u8 ]>> 
```
, whose data is inside the serialized buffer and immediately after the size of the data inside the serialized buffer. And 
```
 slice :: as_mut_ptr () 
```
 gives us that data pointer directly. So, this code computes a pointer to that serialized size field (8 bytes - the size of a 
```
 u64 
```
 - behind the data buffer), and then writes 
```
 new_len 
```
 to it.

 This is reasonableâ¦ as long as the 
```
 data 
```
 actually came from the serialized buffer . Weâll come back to this later .

 At this point weâve updated the serialized buffer, so at exit the runtime will understand that the size of the accountâs data buffer has changed. However, we havenât dealt with the Rust side yet. Slices have a length, and we havenât dealt with the 
```
 & mut [ u8 ] 
```
 slice that is our view into the data from the Rust world. So letâs look at the next chunk:

```

```
 // Then set the new length in the local slice 

 let ptr = & mut *((( self . data . as_ptr () as * const u64 ). offset ( 1 ) as u64 ) as * mut u64 ); 

 * ptr = new_len as u64 ; 

```

```

 That 
```
 as_ptr () 
```
 call is 
```
 RefCell :: as_ptr () 
```
 due to the 
```
 Deref 
```
 impl on 
```
 Rc 
```
. 3 So from 
```
 RefCell ::<& mut [ u8 ]>:: as_ptr () 
```
 we get a 
```
 * mut & mut [ u8 ] 
```
 - a pointer to the slice reference . From here, we turn the pointer into a 
```
 * const u64 
```
 pointer and then offset by 1 
```
 u64 
```
 (so 8 bytes). Finally, we switch the pointer back to being mutable, and write the new length to it.

 Now, if youâre sitting here thinking that this is unnecessarily convoluted and confusing, youâd be right! But weâll get back to that later too, I promise. In summary, weâre writing the new length as a 
```
 u64 
```
 to the region starting 8 bytes from the start of the slice reference (the 
```
 & mut [ u8 ] 
```
). So, what does 
```
 &[ T ] 
```
 look like in Rust?

 According to the reference , itâs completely undefined - there are no guarantees made in the reference, and âType layout can be changed with each compilation. [â¦] we only document what is guaranteed todayâ . But it seems like those pesky language specs arenât stopping Solana developers. In current 
```
rustc
```
, the layout is a data pointer followed by the size; essentially the same as:

```

```
 // C language 

 struct slice_ref { 

 void * ptr ; 

 size_t len ; 

 }; 

```

```

 So at the end of the day we find out that the code is simply writing over the length field in the slice reference. Letâs step back a moment and take a look at all the assumptions we made along the way while executing these two lines (really only one of importance!):

- Slices are laid out in the precise manner described.

- Pointers and 
```
 usize 
```
 are the same width as 
```
 u64 
```
.

- The 
```
 RefCell 
```
 was not borrowed (i.e. we didnât just mutate it while someone else has a reference to its contents).

 Assumption #2 is probably fine when we only care about targeting Solanaâs bytecode machine, but still not a particularly safe assumption to make in case some change happens on the toolchain. And assumption #3 turns out to be a non-issue since we had just done a 
```
 borrow_mut 
```
 of the 
```
 RefCell 
```
 (through 
```
 AccountInfo :: try_borrow_mut_data () 
```
), and 
```
 RefCell 
```
 is not usable between multiple threads 4 , so we already have exclusive access.

 A few more fun things of note that could have gone badly but didnât:

- By reborrowing the pointer (the 
```
&mut *(<value of type *mut u64>)
```
), weâve created a reference with an unbounded lifetime . Rust is free to infer any lifetime for 
```
 ptr 
```
 (including 
```
 'static 
```
); thankfully itâs only used in the next statement and never has a chance to escape.

- Going back to the first statement when we were modifying the data buffer, it turns out we have another lifetime problem: we created a mutable pointer to the data from the 
```
 RefMut 
```
 returned from 
```
 try_borrow_mut_data 
```
, but the 
```
 RefMut 
```
 is dropped at the end of the statement. So, we now have in 
```
 ptr 
```
 a mutable pointer to the 
```
 RefCell 
```
âs data, but the 
```
 RefCell 
```
 thinks that weâre done with our borrow. If we happened to be in a multithreaded scenario with something like a 
```
 Mutex 
```
 instead of a 
```
 RefCell 
```
 (but with otherwise semantically identical code), then a different thread could attempt to borrow between creating 
```
 ptr 
```
 and writing to it and succeed , resulting in us writing while another reference is alive. However, since 
```
 ptr 
```
 is behind the actual data and thus the region it points to is inaccessible through the 
```
 data 
```
 slice, this is still not a problem. I just wanted to highlight how easy it is to mess up borrowing and lifetimes when writing unsafe code.

 Ok, now that weâve understood what the code is trying to do, letâs try to break it, shall we?

## What can go wrong? 

## Contracts 

 Again, itâs quite conspicuous that thereâs no bounds check whatsoever, and additionally, we notice that at no point did we actually touch the data pointer of the slice reference when 
```
 realloc 
```
âing. In other words, when we realloc, all we do is change some size fields, no allocation is happening. So, if we 
```
 realloc 
```
 to some large size, past the end of the buffer of roughly 
```
 MAX_PERMITTED_DATA_INCREASE 
```
 bytes in the serialized buffer from the BPF loader, then weâve got a free out-of-bounds memory write! Using the 
```
 data 
```
 slice, we can write to anything âafterâ our accountâs data in memory. Other accountsâ data are stored adjacent in memory, so itâd be pretty easy to modify the data or lamports. And remember, sizes and indices are unsigned, so whatâs âbehindâ our account in memory is actually just very far âafterâ our account - the address will wrap around the end of the address space.

 There is a check by the BPF loader, however, and it boils down to:

 serialization.rs 
```

```
 324

 if post_len . saturating_sub (* pre_len ) > MAX_PERMITTED_DATA_INCREASE 

 325

 || post_len > MAX_PERMITTED_DATA_LENGTH as usize 

 326

 { 

 327

 return Err ( InstructionError :: InvalidRealloc ); 

 328

 } 

```

```

 MAX_PERMITTED_DATA_INCREASE || post_len > MAX_PERMITTED_DATA_LENGTH as usize{ return Err(InstructionError::InvalidRealloc);}"> 

 But, like the other checks performed by the loader, this check only runs after the contract finishes execution. During execution, the contract is free to make whatever modifications to memory that it wants, since Solanaâs eBPF machine doesnât hook memory accesses in any way.

 The end result is that in order to successfully exploit this bug, an attacker needs a way to change the length back to something valid before the program exits. However, with potentially arbitrary memory access through a mistakenly-
```
 realloc 
```
âd account, this falls in the realm of some old-school pwning - even if we canât use the out-of-bounds access directly, thereâs plenty of pointers in memory that could be of use.

## Not-contracts? 

 Remember when we said that all this code makes sense if the data points to the BPF loaderâs serialized buffer ? Well unfortunately for us, thereâs nothing enforcing that; all the fields on 
```
 AccountInfo 
```
 are public, and so is its 
```
 new 
```
 method (which is nothing more than a thin wrapper around just creating the struct literal yourself ). The 
```
 realloc 
```
 code critically assumes that the memory 8 bytes behind the data buffer is the dataâs length and that we can write to it however we want when reallocâing. So, clearly if we were to create an 
```
 AccountInfo 
```
 ourselves - potentially through the 
```
 Account 
```
 trait , which is hardly documented at all and makes no mention of any prerequisites about the nature of the references that need to be returned - weâd run into problems from pretty much any practical way weâd allocate the 
```
 data 
```
 buffer.

 One long arm of this is 
```
 solana_sdk :: account :: Account 
```
 - in the client SDK. It holds an accountâs data in a 
```
 Vec < u8 > 
```
, and it implements 
```
 solana_program :: account_info :: Account 
```
 (the trait from earlier) - by returning a reference to the contents of that 
```
 Vec 
```
 . So, 
```
 realloc 
```
 writes the size into the 8 bytes right before 
```
 data 
```
; 
```
 data 
```
 is the buffer of a 
```
 Vec 
```
, and so it is the contents of a heap allocation; and, immediately before a heap allocation sits critical metadata. The result? If, for some reason, you construct an 
```
 AccountInfo 
```
 out of an SDK 
```
 Account 
```
 and then realloc it (which admittedly is quite a stretch), then you get heap corruption - something thatâs very likely to lead to remote code execution.

## Remediation 

 Obviously the fix for the main issue at hand is to check that the resize operation remains in-bounds. But how do we know how big is too big?

 The sensible thing to do would be to store the initial size in the 
```
 AccountInfo 
```
â¦ except for the fact that the layout of 
```
 AccountInfo 
```
 is actually part of the ABI between the contract runtime and the loader. ð¤¦ 5 So, with changing 
```
 AccountInfo 
```
 out of the question, the Solana team came up with a different place to stash the information: inside a section of padding in the serialized buffer passed from the runtime. This happened to be next to where the pubkey was stored, which resulted in the creation of this function :

 account_info.rs 
```

```
 74

 /// Return the account's original data length when it was serialized for the 

 75

 /// current program invocation. 

 76

 /// 

 77

 /// # Safety 

 78

 /// 

 79

 /// This method assumes that the original data length was serialized as a u32 

 80

 /// integer in the 4 bytes immediately preceding the serialized account key. 

 81

 pub unsafe fn original_data_len (& self ) -> usize { 

 82

 let key_ptr = self . key as * const _ as * const u8 ; 

 83

 let original_data_len_ptr = key_ptr . offset (- 4 ) as * const u32 ; 

 84

 * original_data_len_ptr as usize 

 85

 } 

```

```

 usize { let key_ptr = self.key as *const _ as *const u8; let original_data_len_ptr = key_ptr.offset(-4) as *const u32; *original_data_len_ptr as usize}"> 

 Itâs marked 
```
 unsafe 
```
, properly documented, but thereâs just one problem: we need this for 
```
 realloc 
```
, which originally was not 
```
 unsafe 
```
. So, in the name of not breaking API compatibility, the Solana team just threw the call in an 
```
 unsafe 
```
 block and added a doc comment - adding to the small pile of functions that are actually unsafe but arenât marked as such for API compatibility reasons. 6 

## Towards safer 
```
unsafe
```

 Letâs circle back to that main 
```
 unsafe 
```
 block inside 
```
 realloc 
```
 for a bit, shall we? As a reminder, it looks like this :

 account_info.rs 
```

```
 127

 // realloc 

 128

 unsafe { 

 129

 // First set new length in the serialized data 

 130

 let ptr = self . try_borrow_mut_data ()?. as_mut_ptr (). offset (- 8 ) as * mut u64 ; 

 131

 * ptr = new_len as u64 ; 

 132

 133

 // Then set the new length in the local slice 

 134

 let ptr = & mut *((( self . data . as_ptr () as * const u64 ). offset ( 1 ) as u64 ) as * mut u64 ); 

 135

 * ptr = new_len as u64 ; 

 136

 } 

```

```

 Weâve seen how we could have run into all sorts of issues here, with the usage of slice layout details, the reborrow creating an unbounded lifetime, and the 
```
 RefCell 
```
 borrow not accurately representing the actual usage of its contents. We can do better than this.

 First, letâs deal with the 
```
 RefCell 
```
 borrowing issue. When we 
```
 try_borrow_mut_data 
```
, we get a 
```
 RefMut 
```
 back, which represents our borrow of the 
```
 RefCell 
```
âs data. The fix here is simple: keep that 
```
 RefMut 
```
 around and use it to access the data, instead of using 
```
 RefCell :: as_ptr 
```
. Next, the slice; again, the fix is simple. Instead of attempting to modify just the length field, and resorting to using layout information to do so since Rust slices are immutable, we can simply construct a new slice reference and set that. The Rust compiler 7 is smart enough to realize that the only thing changing is the length field, and so only emits the code to set the length 8 . So then we get:

 account_info.rs 
```

```
 1

 let mut slice = self . try_borrow_mut_data ()?; 

 2

 3

 // First set new length in the serialized data 

 4

 let ptr = unsafe { slice . as_mut_ptr (). offset (- 8 ) } as * mut u64 ; 

 5

 unsafe { * ptr = new_len as u64 }; 

 6

 7

 // Then set the new length in the local slice 

 8

 * slice = unsafe { std :: slice :: from_raw_parts_mut ( slice . as_mut_ptr (), new_len ) }; 

```

```

 No more pointer casting except for the one place that actually needs it (since the ABI for the serialized buffer uses a 
```
 u64 
```
 and not a 
```
 usize 
```
 for the size field, given that 
```
 usize 
```
 is architecture-dependent), and no dependency on slice reference internals! 9 

## Footnotes 

- 
 I find it helpful to view owning an 
```
 Rc < T > 
```
 as holding a shared reference to the underlying 
```
 T 
```
 (stored in the magical land of I-donât-need-to-care-about-this-object-not-living-long-enough known as the heap). Owning the reference ensures that the actual data stays alive, however all you have is a reference to the 
```
 T 
```
 (through the 
```
 Deref < Target = T > 
```
 impl) - not ownership of the 
```
 T 
```
 . In short, owning an 
```
 Rc < T > 
```
 is owning a (shared, read-only) reference to 
```
 T 
```
, not owning 
```
 T 
```
 directly like with 
```
 Box < T > 
```
. â© 

- 
 The 
```
 lamports 
```
 field is very similar, for essentially the same reason - we need to be able to mutate it, but it is also shared between multiple instances of the same account. â© 

- 
 Remember also that 
```
 RefCell 
```
 itself doesnât behave like a reference; you need to actually get one through 
```
 borrow 
```
 and frie nds . â© 

- 
 
```
 ! Send + ! Sync 
```
 â© 

- 
 Note that this is a terrible idea for yet another reason: 
```
 AccountInfo 
```
 is not declared with 
```
 #[ repr ( C )] 
```
 , meaning that, once again, weâre dealing with no layout guarantees. But thanks to the power of blockchain, fixing this ABI interface breaks the entire chain since old contracts will no longer work. So, weâre stuck with cobbling together some kind of interface to the specific layout of the specific 
```
rustc
```
 versions used to build on-chain code for all eternityâ¦ â© 

- 
 The last three - all related to each other - donât even have the comment until version 1.11, which isnât even on mainnet as of the time of writing. â© 

- 
 Actually, itâs LLVM that does the optimization. â© 

- 
 Click here for a Compiler Explorer link showing this - note that the code for both implementations is almost identical. And yes, itâs x86_64 and not eBPF, but unfortunately Compiler Explorer doesnât have Rust 
```
libcore
```
 available for other architectures yet. â© 

- 
 The astute reader may have noticed that 
```
 from_raw_parts_mut 
```
 still returns an unbounded lifetime (notice in the signature 
```
 unsafe fn from_raw_parts_mut < 'a , T >( data : * mut T , len : usize ) -> & 'a mut [ T ] 
```
, the lifetime parameter 
```
 'a 
```
 does not appear in the arguments). However, we immediately constrain the lifetime by assigning it to 
```
 * slice 
```
, which is 
```
 & 'info [ u8 ] 
```
 (where 
```
 'info 
```
 is the lifetime parameter of the 
```
 AccountInfo 
```
 struct) - this is exactly the lifetime we started with. â©

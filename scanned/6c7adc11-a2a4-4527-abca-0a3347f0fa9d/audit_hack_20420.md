# [H] OtterSec: Solana formal verification: a case study

## Summary
Severity: High
Published: Thu, 26 Jan 2023
Source: https://osec.io/blog/formally-verifying-solana-programs/
Type: security-research

## Details
## Solana formal verification: a case study

 Harrison Green Jan 26, 2023 #solana #report We present a novel framework for formal verification of Solana Anchor programs â and a case study application to the Squads multisig.

## Introduction 

 Since the early days of computing, bugs have crept their way into programs and wreaked havoc on the intentions of the programmer. Logical fallacies, race conditions, or simple typos could manifest as crashes or lie undetected, silently breaking the functionality of the host program.

 When your program is connected to the internet, there is the new risk that bugs may introduce security holes into your system. Even simple buffer overflows can be exploited by skilled attackers to compromise the integrity of your program.

 In the world of Web3 we create programs that talk to strangers and control millions of dollars ð¤. Bugs in these programs are some of the juiciest ; anonymous attackers that can find and exploit them will walk away with potentially hundreds of millions of dollars .

 At OtterSec we are highly skilled in pest control â finding and squashing bugs before they are exploited by less well-intentioned hackers. We are constantly striving to improve our techniques and develop new technologies that aid in our auditing processes.

 Recently we were contacted by the Squads team to explore how formal verification could be used to verify security-critical properties of Solana programs. We were really excited about this opportunity and have been developing a prototype with the Squads Multisig Program as our main case study.

 We now have a (mostly) working prototype that can be used to formally verify critical properties of Solana programs in order to ensure a higher level of security. Our tool integrates with anchor-lang and provides new APIs to specify invariants for your Solana code. It then autogenerates proof harnesses which are verified with the Kani Rust Verifier . Additionally, we are implementing a formal-verification-friendly runtime SDK layer that accelerates the expensive process of running formal verification tools on complex code.

 In this blog post, weâre excited to share our progress and the challenges weâve encountered during the process. We will describe the main concepts behind bounded model checking (our formal verification method of choice) and explain how weâve applied these concepts to Solana.

 Note (Get in touch) If youâre interested in learning more or getting your own programs formally verified, let us know! Weâd be excited to chat with you â fill out this form or email us at contact@osec.io .

## Contents 

- Formal verification with bounded model checking
 
- Overview

- A simple example

- Loop bounds & path explosion

- Kani model checker

- Specification: how can we describe what we want our program to do?

- Verification: how do we check that our model is correct?

- Case study: Squads Multisig

- Challenges of formal verification on Solana

- Conclusion

## Formal verification with bounded model checking 

## Overview 

 Formal verification is the process of using a formal specification to verify the correctness of a system. In this case, the systems we are verifying are programs written in Rust that run on the Solana blockchain.

 There are many different flavors of formal verification; however, in this research we are using bounded model checking (BMC) .

 In short, the idea of BMC is to execute our program symbolically rather than concretely . Instead of actually performing an add when we see the line 
```
 int x = a + b 
```
, we store the symbolic expression 
```
 x == a + b 
```
. We do this for every line, and once we reach the end of the program we have compiled a huge list of symbolic expressions. At this point, we can feed these expressions to an SMT solver along with a correctness property P P P in order to check if our program satisfies this property.

 If we hit a branch as we are tracing the program, we will take both sides of the branch, adding the positive branch condition as a constraint to one side and the negative condition to the other side.

## A simple example 

 As an example, consider the following function:

```

```
 1

 int foo ( int x ) { 

 2

 int y = x + 3 ; 

 3

 int z ; 

 4

 if ( y > 100 ) { 

 5

 z = y * 2 ; 

 6

 } else { 

 7

 z = y + 1 ; 

 8

 } 

 9

 10

 // Property P: 

 11

 assert ( z != 105 ); 

 12

 } 

```

```

 100) { z = y * 2; } else { z = y + 1; } // Property P: assert(z != 105);}"> 

 This function takes an input 
```
x
```
 and does some computation. At the end of the program, the property we want to verify is that 
```
 z != 105 
```
.

 With BMC, we could trace this program and derive the following constraints:

 Positive branch:

```

```
 y == x + 3 

 y > 100 

 z == y * 2 

```

```

 100z == y * 2"> 

 Negative branch:

```

```
 y == x + 3 

 y <= 100 

 z == y + 1 

```

```

 Using the z3 SMT solver, we could check both of these cases like so:

```

```
 1

 from z3 import * 

 2

 3

 x = Int ( 'x' ) 

 4

 y = Int ( 'y' ) 

 5

 z = Int ( 'z' ) 

 6

 7

 # Positive branch: 

 8

 s = Solver () 

 9

 s . add ( y == x + 3 ) 

 10

 s . add ( y > 100 ) 

 11

 s . add ( z == y * 2 ) 

 12

 13

 # check if we can violate the correctness property 

 14

 s . add ( Not ( z != 105 )) 

 15

 print ( s . check ()) # "unsat" 

 16

 17

 # Negative branch: 

 18

 s = Solver () 

 19

 s . add ( y == x + 3 ) 

 20

 s . add ( y <= 100 ) 

 21

 s . add ( z == y + 1 ) 

 22

 23

 # check if we can violate the correctness property 

 24

 s . add ( Not ( z != 105 )) 

 25

 print ( s . check ()) # "unsat" 

```

```

 100)s.add(z == y * 2)# check if we can violate the correctness propertys.add(Not(z != 105))print(s.check()) # "unsat"# Negative branch:s = Solver()s.add(y == x + 3)s.add(y 

 Both of these cases return 
```
unsat
```
, meaning z3 could not find a way to violate the correctness property, hence our program is correct according to this property.

## Loop bounds & path explosion 

 As you may have noticed, BMC requires us to take every branch in the program. To be sure that our property holds, we need to check every possible route through the program. If we have 10 branches in a row we might need to test 2 10 2^{10} 2 10 paths! And if our program has loops, we may need to check an infinite number of paths because the loop branches backward. This might take a whileâ¦

 This is where the âboundedâ part of âbounded model checkingâ applies. Rather than unroll an infinite number of loops, we can set a loop bound and also verify that it is not possible to loop more than the loop bound.

 While this technique of bounding loops makes the problem tractable, it is still expensive to run BMC on very large programs due to the problem of path explosion. As our program gets larger, the number of possible paths scales potentially exponentially.

 One of the main challenges we will discuss later is how to address this problem of path explosion in the context of Solana Rust programs.

## Kani model checker 

 For our research with formally verifying Solana programs, we are using the Kani Rust Verifier : an open-source, bit-precise model checker for Rust created at AWS. Under the hood, Kani uses the C Bounded Model Checker (CBMC) to do the heavy lifting.

 Kani allows you to write proof harnesses which can invoke Rust functions with symbolic values. These harnesses can 
```
 assume 
```
 and 
```
 assert 
```
 certain conditions about these symbolic values, and then you can verify that a proof harness holds via the 
```
 cargo kani 
```
 tool (which compiles your proof harness and runs BMC).

## Specification: how can we describe what we want our program to do? 

 And what even do we want it to do? 

 A fundamental challenge with any formal verification framework is specifying what the âcorrectâ behavior should be.

 In natural language, we can describe a few good properties for some example Solana programs:

- âIt should not be possible to steal money via a swap programâ

- âA multisig should never get into a state where you canât sign anything â

- âUser funds in a staking protocolâ

 These are the types of properties you can tell your human auditors , but these English phrases are not particularly useful for automated verification techniques . 1 

 Instead, we need to be able to specify in code what properties we want to check. Ideally, we could define invariants that fit nicely into something like an 
```
 assert 
```
 statement.

## Solana invariants 

 In the context of Solana programs, we define two different types of properties that we would like to verify: instruction invariants and account invariants .

### Instruction invariants 

 An instruction invariant specifies sufficient conditions for an instruction to succeed (or fail). These are specified as 
```
 succeeds_if 
```
 or 
```
 errors_if 
```
 macro annotations on the instruction handler.

 In Solana, when an instruction fails, the entire transaction is reverted. Failing an instruction on purpose is commonly used as a form of access control; invalid accounts, bad state, etc. will cause an instruction to fail and get reverted.

 For example, say we have a 
```
 Withdraw 
```
 instruction that lets a user withdraw some tokens. A security-critical property we may want to verify is that the user cannot withdraw more tokens than their current balance.

 Using our tool, you could specify the following 
```
 errors_if 
```
 property on your instruction handler:

```

```
 #[ errors_if ( 

 ctx . user . balance < amount 

 )] 

 fn withdraw ( ctx : Context < Withdraw >, amount : u64 ) -> Result <()> { 

 ... 

 } 

```

```

 , amount: u64) -> Result { ...}"> 

 Note The 
```
 errors_if 
```
 expression specifies sufficient but not necessary conditions for an instruction to fail, i.e. it imposes a strong lower bound on what the requirements are for an instruction to fail.

 Another example is that for crank functions â run by unauthenticated users to advance the state of the system â you may want to prove that they never fail. In that case, you could specify an invariant like the following:

```

```
 #[ succeeds_if ( true )] 

 fn my_crank ( ctx : Context < Crank >) -> Result <()> { 

 ... 

 } 

```

```

 ) -> Result { ...}"> 

 With this invariant, you could prove that the function always returns 
```
 Ok 
```
. This type of construction could help avoid possible denial-of-service attacks if a crank could get âstuck.â

 Note that 
```
 succeeds_if 
```
 and 
```
 errors_if 
```
 are both implications and not biconditionals. That is, a function may succeed even if 
```
 succeeds_if 
```
 is not satisfied, and a function may fail even if 
```
 errors_if 
```
 is not satisfied. If you want to prove the exact condition required for an instruction to succeed, you could use a form like the following:

```

```
 fn my_invariant (...) -> bool { ... } 

 #[ succeeds_if ( my_invariant (...))] 

 #[ errors_if (! my_invariant (...))] 

 fn my_instruction ( ctx : Context <...>) -> Result <()> { 

 ... 

 } 

```

```

 bool { ... }#[succeeds_if(my_invariant(...))]#[errors_if(!my_invariant(...))]fn my_instruction(ctx: Context ) -> Result { ...}"> 

 Note that in practice, it is usually not necessary (or useful) to find the exact condition; rather, we can achieve the security properties we want purely by proving upper and lower bounds on instruction success.

### Account invariants 

 The other type of invariant is an account invariant . This invariant describes some property of an account that should always hold.

 In our tool, we verify that the account invariant holds after every instruction that could modify the account data (i.e. if the account is 
```
mut
```
 or 
```
init
```
).

 For example, given a mock 
```
 UserStatement 
```
 account that represents how much a user owns and owes, we could write an invariant that asserts that the net balance is positive:

```

```
 1

 #[ account ] 

 2

 #[ invariant ( 

 3

 self . assets >= self . liabilities 

 4

 )] 

 5

 struct UserStatement { 

 6

 pub owner : Pubkey , 

 7

 pub assets : u64 , 

 8

 pub liabilities : u64 , 

 9

 } 

```

```

 = self.liabilities)]struct UserStatement { pub owner: Pubkey, pub assets: u64, pub liabilities: u64,}"> 

 Our tool automatically generates the relevant harnesses to ensure that this property holds every time an account of type 
```
 UserStatement 
```
 is created or modified.

 In another example, we developed the following invariant for the Squads Multisig wallet account:

```

```
 1

 #[ account ] 

 2

 #[ invariant ( 

 3

 ! self . keys . is_empty () 

 4

 && ( self . keys . len () <= u16 :: MAX as usize ) 

 5

 && ( self . threshold >= 1 ) 

 6

 && ( self . threshold as usize <= self . keys . len ()) 

 7

 )] 

 8

 pub struct Ms { 

 9

 pub threshold : u16 , // threshold for signatures 

 10

 pub authority_index : u16 , // index to seed other authorities under this multisig 

 11

 pub transaction_index : u32 , // look up and seed reference for transactions 

 12

 pub ms_change_index : u32 , // the last executed/closed transaction 

 13

 pub bump : u8 , // bump for the multisig seed 

 14

 pub create_key : Pubkey , // random key(or not) used to seed the multisig pda 

 15

 pub allow_external_execute : bool , // allow non-member keys to execute txs 

 16

 pub keys : Vec < Pubkey >, // keys of the members 

 17

 } 

```

```

 = 1) && (self.threshold as usize , // keys of the members}"> 

 Here we are verifying multiple things at once:

- 
```
 ! self . keys . is_empty () 
```
: ensures there is at least one member.

- 
```
 self . keys . len () <= u16 :: MAX as usize 
```
: sets an upper limit of 65535 members.

- 
```
 self . threshold >= 1 
```
: ensures we always need at least one member to sign (a threshold of zero would require no signers!).

- 
```
 self . threshold as usize <= self . keys . len () 
```
: ensures we always have enough potential members to sign; if the threshold was greater than the number of keys, no one could sign.

## Verification: how do we check that our model is correct? 

 Now that we have defined the specific instruction and account invariants, we need to generate proof harnesses on which we can run bounded model checking. Our tool does this automagically for anchor-lang programs.

 Specifically, for a given 
```
 Context < T > 
```
 with incoming accounts of type (
```
init
```
/
```
mut
```
) and outgoing accounts of type (
```
mut
```
/
```
close
```
), we define a 
```
 pre_condition 
```
 and 
```
 post_condition 
```
 expression that is a conjunction of all of the incoming and outgoing account invariants:

 P 0 : = â a c c Â â Â incoming ( c t x ) invariant ( a c c ) P0 := \bigwedge_{acc\ \in\ \text{incoming}(ctx)}{\text{invariant}(acc)} P 0 := â a cc Â â Â incoming ( c t x ) â invariant ( a cc ) 

 P 1 : = â a c c Â â Â outgoing ( c t x ) invariant ( a c c ) P1 := \bigwedge_{acc\ \in\ \text{outgoing}(ctx)}{\text{invariant}(acc)} P 1 := â a cc Â â Â outgoing ( c t x ) â invariant ( a cc ) 

 Our instruction invariants are represented as:

- S S S : 
```
 succeeds_if 
```

- E E E : 
```
 errors_if 
```

 And K K K represents whether the instruction actually succeeds (i.e. invoking the handler returned an 
```
 Ok 
```
, not an 
```
 Err 
```
).

 In order to verify these conditions, we need to verify three cases:

## Account invariants 

 After we execute an instruction, either the function should error and be reverted ( Â¬ K \neg K Â¬ K ) or the account post-invariants should hold ( P 1 P1 P 1 ). Furthermore, we can assume that before executing a function, the account pre-invariants ( P 0 P0 P 0 ) should hold, since we will verify all of the functions eventually.

 So we are trying to prove that ( P 0 â§ K ) â P 1 (P0 \land K) \rightarrow P1 ( P 0 â§ K ) â P 1 .

 We can construct a proof harness like the following:

```

```
 assume ( P0 ) 

 res = instruction_handler ( ... ) 

 assert ( ! K || P1 ) 

```

```

 By itself, this harness doesnât actually prove much. For example, if the instruction fails every time, this proof will still work. However, in conjunction with the two subsequent proofs, we can be assured that the instruction will actually succeed when we expect it to.

## Positive instruction invariant 

 Next, we need to prove that 
```
 succeeds_if 
```
 is a sufficient condition for instruction success, i.e. S â K S \rightarrow K S â K .

 Just like before, we can construct a proof harness:

```

```
 assume ( S ) 

 res = instruction_handler ( ... ) 

 assert ( K ) 

```

```

 This proof assures that whenever 
```
 succeeds_if 
```
 is satisfied, the instruction will succeed. However, remember that since this is not a biconditional, the instruction may also succeed even if 
```
 succeeds_if 
```
 is not satisfied . To specify explicit error conditions, we need our third and final proof.

## Negative instruction invariant 

 Finally, we want to prove that 
```
 errors_if 
```
 is a sufficient condition for instruction failure, i.e. E â Â¬ K E \rightarrow \neg K E â Â¬ K .

 This harness looks just like the previous one:

```

```
 assume ( E ) 

 res = instruction_handler ( ... ) 

 assert ( ! K ) 

```

```

 With these three harnesses, we are now able to formally verify that instructions succeed or fail when we expect them to and that the account invariants we expect are always being preserved.

## Case study: Squads Multisig 

 During our research, we focused on formally verifying aspects of the Squads Multisig Program .

 The program defines a multisig account (
```
 Ms 
```
) which has multiple members. These members can propose and then vote on transactions to execute on behalf of the multisig. If at least some 
```
threshold
```
 of members vote yes, the transaction will be invoked. Additionally, there is functionality to add/remove users and update the threshold.

 In practice, this structure provides a useful way to distribute authority across a group of individuals. From a formal verification perspective, it has both stateless and stateful features and constraints that provided a good testbed for our tooling.

 In this section, we will go through a few examples of properties that we can verify on this program:

- Incrementally verifying minimum requirements to create a multisig

- Verify threshold requirements

- Verify requirements to remove a member

- Safety guarantees

## 1. Incrementally verifying minimum requirements to create a multisig 

 Suppose we want to verify the minimum requirements to create a multisig, i.e. the 
```
 succeeds_if 
```
 expression.

 Creating a multisig (
```
 Ms 
```
) requires invoking the 
```
 create 
```
 instruction:

 squads-mpl 
```

```

 15 collapsed lines 

 1

 #[ derive ( Accounts )] 

 2

 #[ instruction ( threshold : u16 , create_key : Pubkey , members : Vec < Pubkey >)] 

 3

 pub struct Create < 'info > { 

 4

 #[ account ( 

 5

 init , 

 6

 payer = creator , 

 7

 space = Ms :: SIZE_WITHOUT_MEMBERS + ( members . len () * 32 ), 

 8

 seeds = [ b"squad" , create_key . as_ref (), b"multisig" ], bump 

 9

 )] 

 10

 pub multisig : Account < 'info , Ms >, 

 11

 12

 #[ account ( mut )] 

 13

 pub creator : Signer < 'info >, 

 14

 pub system_program : Program < 'info , System >, 

 15

 } 

 16

 17

 pub fn create ( 

 18

 ctx : Context < Create >, 

 19

 threshold : u16 , 

 20

 create_key : Pubkey , 

 21

 members : Vec < Pubkey >, 

 22

 ) -> Result <()> { 

 23

 // sort the members and remove duplicates 

 24

 let mut members = members ; 

 25

 members . sort (); 

 26

 members . dedup (); 

 27

 28

 // check we don't exceed u16 

 29

 let total_members = members . len (); 

 30

 if total_members < 1 { 

 31

 return err! ( MsError :: EmptyMembers ); 

 32

 } 

 33

 34

 // make sure we don't exceed u16 on first call 

 35

 if total_members > usize :: from ( u16 :: MAX ) { 

 36

 return err! ( MsError :: MaxMembersReached ); 

 37

 } 

 38

 39

 // make sure threshold is valid 

 40

 if usize :: from ( threshold ) < 1 || usize :: from ( threshold ) > total_members { 

 41

 return err! ( MsError :: InvalidThreshold ); 

 42

 } 

 43

 44

 ctx . accounts . multisig . init ( 

 45

 threshold , 

 46

 create_key , 

 47

 members , 

 48

 * ctx . bumps . get ( "multisig" ). unwrap (), 

 49

 ) 

 50

 } 

```

```

 )]pub struct Create { #[account( init, payer = creator, space = Ms::SIZE_WITHOUT_MEMBERS + (members.len() * 32), seeds = [b"squad", create_key.as_ref(), b"multisig"], bump )] pub multisig: Account , #[account(mut)] pub creator: Signer , pub system_program: Program ,}pub fn create( ctx: Context , threshold: u16, create_key: Pubkey, members: Vec ,) -> Result { // sort the members and remove duplicates let mut members = members; members.sort(); members.dedup(); // check we don't exceed u16 let total_members = members.len(); if total_members usize::from(u16::MAX) { return err!(MsError::MaxMembersReached); } // make sure threshold is valid if usize::from(threshold) total_members { return err!(MsError::InvalidThreshold); } ctx.accounts.multisig.init( threshold, create_key, members, *ctx.bumps.get("multisig").unwrap(), )}"> 

 We can start by testing an empty 
```
 succeeds_if 
```
 (this will default to 
```
 true 
```
):

```

```
 #[ succeeds_if ()] 

 pub fn create (...) { ... } 

```

```

 Running the solver, we get:

```

```
 ... 

 VERIFICATION:- FAILED 

 Verification Time: 6.404167s 

```

```

 This means that 
```
 true 
```
 does not imply that the function will succeed (which is expected looking at the implementation above).

 We can ask the solver to produce a counterexample:

```

```
 threshold: 33764 

 create_key: ... 

 members: SparseVec { size: 19 } 

```

```

 In this case, we can see that the threshold is invalid; it should not be larger than the number of members.

 Note (SparseVec) Note also that the verifier decided to use a 
```
 SparseVec 
```
, which is one of our custom vec implementations. In this case, the code we are verifying doesnât actually read or write to the vector, and so we can model it simply as a symbolic size (with no data).

 Using a sparse vec rather than a concrete vec is generally preferred, as it speeds up computation and allows us to model arbitrarily sized vecs. 
```
push
```
 and 
```
pop
```
 are stubbed out to simply panic for the 
```
 SparseVec 
```
, and if this code tried to do that we would fall back to the concrete 
```
 Vec 
```
 type.

 We can add this to our constraint and try again:

```

```
 #[ succeeds_if ( 

 ( threshold as usize ) <= members . len () 

 )] 

 pub fn create (...) { ... } 

```

```

 Verification failed again! This time we get a different counterexample:

```

```
 threshold: 0 

 create_key: ... 

 members: SparseVec { size: 19 } 

```

```

 Aha! The threshold cannot be 0 eitherâ¦ Letâs try again:

```

```
 #[ succeeds_if ( 

 ( threshold as usize ) <= members . len () 

 && threshold != 0 

 )] 

 pub fn create (...) { ... } 

```

```

 A third counterexample:

```

```
 threshold: 4 

 create_key: ... 

 members: SparseVec { size: 536870920 } 

```

```

 Here we see the size of our 
```
members
```
 vec is huge! We need to constrain that to be less than 
```
 u16 :: MAX 
```
:

```

```
 #[ succeeds_if ( 

 ( threshold as usize ) <= members . len () 

 && ( threshold != 0 ) 

 && ( members . len () <= ( u16 :: MAX as usize )) 

 )] 

 pub fn create (...) { ... } 

```

```

 And now we get:

```

```
 VERIFICATION:- SUCCESSFUL 

 Verification Time: 6.6634517s 

```

```

 ð¥³ð¥³ð¥³

 The attentive reader may have noticed that we didnât need to verify this condition:

```

```
 if total_members < 1 { 

 return err! ( MsError :: EmptyMembers ); 

 } 

```

```

 In this case, this is actually redundant because if 
```
 members . len () == 0 
```
 then our threshold would also have to be 
```
0
```
 (and our 
```
threshold
```
 is not allowed to be 
```
0
```
). The solver realizes that this situation is impossible and therefore the expression we have above is sufficient!

## 2. Verify threshold requirements 

 A critical security property for multisigs is that the threshold should never be zero (which would let anyone issue transactions), and the threshold should never be greater than the number of members (which would let nobody issue transactions).

 Unlike the previous example, we want to verify this in all cases, i.e. any instruction that could mutate the multisig account.

 In this case, we want to model this as an invariant on the 
```
 Ms 
```
 account struct:

```

```
 1

 #[ account ] 

 2

 #[ derive ( Clone , Debug )] 

 3

 #[ invariant ( 

 4

 ( self . threshold >= 1 ) 

 5

 && ( self . threshold as usize <= self . keys . len ()) 

 6

 )] 

 7

 pub struct Ms { 

 8

 pub threshold : u16 , // threshold for signatures 

 9

 pub authority_index : u16 , // index to seed other authorities under this multisig 

 10

 pub transaction_index : u32 , // look up and seed reference for transactions 

 11

 pub ms_change_index : u32 , // the last executed/closed transaction 

 12

 pub bump : u8 , // bump for the multisig seed 

 13

 pub create_key : Pubkey , // random key(or not) used to seed the multisig pda 

 14

 pub allow_external_execute : bool , // allow non-member keys to execute txs 

 15

 pub keys : Vec < Pubkey >, // keys of the members 

 16

 } 

```

```

 = 1) && (self.threshold as usize , // keys of the members}"> 

 Our verification framework will generate an invariant harness for each instruction. Instructions that can potentially modify the 
```
 Ms 
```
 object will be checked to ensure that the invariant still holds after modification.

 Letâs try this on the 
```
 create 
```
 instruction that weâve already seen:

```

```
 VERIFICATION:- SUCCESSFUL 

 Verification Time: 6.8006988s 

```

```

 To ensure this is working, we can test by commenting out this check from 
```
 create 
```
:

```

```
 // if usize::from(threshold) < 1 || usize::from(threshold) > total_members { 

 // return err!(MsError::InvalidThreshold); 

 // } 

```

```

 total_members {// return err!(MsError::InvalidThreshold);// }"> 

 And run again:

```

```
 VERIFICATION:- FAILED 

 Verification Time: 8.245743s 

```

```

 We get the following counterexample:

```

```
 Account { 

 account : Ms { 

 threshold : 32768 , 

 authority_index : 1 , 

 transaction_index : 0 , 

 ms_change_index : 0 , 

 bump : 0 , 

 create_key : ..., 

 allow_external_execute : false , 

 keys : SparseVec { 

 size : 5112 , 

 }, 

 }, 

 info : AccountInfo { ... }, 

 } 

```

```

 Here we see that the 
```
threshold
```
 of the newly created 
```
 Ms 
```
 account is larger than the number of keys (5112), which breaks our struct invariant.

## 3. Verify requirements to remove a member 

 Now that weâve seen both 
```
 succeeds_if 
```
 and 
```
 invariant 
```
, letâs take a look at the 
```
 remove_member () 
```
 function:

 squads-mpl 
```

```

 14 collapsed lines 

 1

 #[ derive ( Accounts , Debug )] 

 2

 pub struct MsAuth < 'info > { 

 3

 #[ account ( mut )] 

 4

 multisig : Box < Account < 'info , Ms >>, 

 5

 #[ account ( 

 6

 mut , 

 7

 seeds = [ 

 8

 b"squad" , 

 9

 multisig . create_key . as_ref (), 

 10

 b"multisig" 

 11

 ], bump = multisig . bump 

 12

 )] 

 13

 pub multisig_auth : Signer < 'info >, 

 14

 } 

 15

 16

 pub fn remove_member ( ctx : Context < MsAuth >, old_member : Pubkey ) -> Result <()> { 

 17

 // if there is only one key in this multisig, reject the removal 

 18

 if ctx . accounts . multisig . keys . len () == 1 { 

 19

 return err! ( MsError :: CannotRemoveSoloMember ); 

 20

 } 

 21

 ctx . accounts . multisig . remove_member ( old_member )?; 

 22

 23

 // if the number of keys is now less than the threshold, adjust it 

 24

 if ctx . accounts . multisig . keys . len () < usize :: from ( ctx . accounts . multisig . threshold ) { 

 25

 let new_threshold : u16 = ctx . accounts . multisig . keys . len (). try_into (). unwrap (); 

 26

 ctx . accounts . multisig . change_threshold ( new_threshold )?; 

 27

 } 

 28

 let new_index = ctx . accounts . multisig . transaction_index ; 

 29

 ctx . accounts . multisig . set_change_index ( new_index ) 

 30

 } 

```

```

 { #[account(mut)] multisig: Box >, #[account( mut, seeds = [ b"squad", multisig.create_key.as_ref(), b"multisig" ], bump = multisig.bump )] pub multisig_auth: Signer ,}pub fn remove_member(ctx: Context , old_member: Pubkey) -> Result { // if there is only one key in this multisig, reject the removal if ctx.accounts.multisig.keys.len() == 1 { return err!(MsError::CannotRemoveSoloMember); } ctx.accounts.multisig.remove_member(old_member)?; // if the number of keys is now less than the threshold, adjust it if ctx.accounts.multisig.keys.len() 

 First, letâs establish the 
```
 succeeds_if 
```
 condition. We can do this either interactively, following counterexamples like in the first example, or we can guess what a sufficient condition might be:

```

```
 #[ succeeds_if ( 

 ctx . accounts . multisig . keys . len () > 1 

 )] 

 fn remove_member (...) { ... } 

```

```

 1)]fn remove_member(...) { ... }"> 

 And for now, letâs remove the invariant on the 
```
 Ms 
```
 account:

```

```
 #[ invariant ()] 

 pub struct Ms { ... } 

```

```

 Letâs test this!

 Our 
```
 succeeds_if 
```
 harness produces:

```

```
 VERIFICATION:- SUCCESSFUL 

 Verification Time: 28.119272s 

```

```

 This tells us that if our multisig has at least two keys, then the instruction will succeed.

 However, remember that since 
```
 succeeds_if 
```
 represents just the sufficient conditions, there may be other cases where the function succeeds.

 Suppose we want to be sure that this condition is the only condition in which the function will succeed (i.e. âthe function will succeed if and only if the multisig has at least two keysâ ). We could attempt to verify the other side of this with an 
```
 errors_if 
```
 macro such as:

```

```
 #[ succeeds_if ( 

 ctx . accounts . multisig . keys . len () > 1 

 )] 

 #[ errors_if ( 

 ctx . accounts . multisig . keys . len () <= 1 

 )] 

 fn remove_member (...) { ... } 

```

```

 1)]#[errors_if( ctx.accounts.multisig.keys.len() 

 Letâs test this â we just need to run the new 
```
 errors_if 
```
 harness:

```

```
 VERIFICATION:- FAILED 

 Verification Time: 31.900913s 

```

```

 Hmm, this verification failed! Letâs look at the counterexample. The multisig it is trying to remove a member from looks like:

```

```
 Account { 

 account : Ms { 

 threshold : 0 , 

 authority_index : 0 , 

 transaction_index : 0 , 

 ms_change_index : 0 , 

 bump : 0 , 

 create_key : ..., 

 allow_external_execute : false , 

 keys : Vec { 

 data : ..., 

 size : 0 , 

 }, 

 }, 

 info : AccountInfo { ... }, 

 } 

```

```

 Interestingly, the multisig has 0 keys and yet this instruction does not error. Letâs take a closer look to figure out why.

 Inside our handler, we see that it only checks if the number of keys exactly equals 1. Otherwise, it invokes 
```
 Ms :: remove_member () 
```
:

```

```
 if ctx . accounts . multisig . keys . len () == 1 { 

 return err! ( MsError :: CannotRemoveSoloMember ); 

 } 

 ctx . accounts . multisig . remove_member ( old_member )?; 

```

```

 In that function, it checks if the member to remove is contained in that multisig (with 
```
 Ms :: is_member () 
```
), and if it is not, it simply skips the removal and returns 
```
 Ok (()) 
```
:

 state.rs 
```

```
 1

 pub fn remove_member (& mut self , member : Pubkey ) -> Result <()> { 

 2

 if let Some ( ind ) = self . is_member ( member ) { 

 3

 self . keys . remove ( ind ); 

 4

 if self . keys . len () < usize :: from ( self . threshold ) { 

 5

 self . threshold = self . keys . len (). try_into (). unwrap (); 

 6

 } 

 7

 } 

 8

 Ok (()) 

 9

 } 

```

```

 Result { if let Some(ind) = self.is_member(member) { self.keys.remove(ind); if self.keys.len() 

 Inside 
```
 Ms :: is_member () 
```
, we see that it performs a 
```
 binary_search () 
```
 on the keys vec and returns the index or 
```
 None 
```
:

 state.rs 
```

```
 1

 pub fn is_member (& self , member : Pubkey ) -> Option < usize > { 

 2

 match self . keys . binary_search (& member ) { 

 3

 Ok ( ind ) => Some ( ind ), 

 4

 _ => None , 

 5

 } 

 6

 } 

```

```

 Option { match self.keys.binary_search(&member) { Ok(ind) => Some(ind), _ => None, }}"> 

 Since the vec has size zero, this will just return 
```
 None 
```
.

 So interestingly, a 
```
keys
```
 vec of size 0 is actually a sufficient condition to execute 
```
 remove_member () 
```
. However, would it ever actually happen? Well, we know from before that when we create the multisig, the threshold must be less than or equal to the number of keys and also greater than zero. So in any valid multisig, the number of keys should never be zero.

 We can represent this validity with a struct invariant. In fact, the invariant we defined earlier will be sufficient:

```

```
 #[ invariant ( 

 ( self . threshold >= 1 ) 

 && ( self . threshold as usize <= self . keys . len ()) 

 )] 

 pub struct Ms { ... } 

```

```

 = 1) && (self.threshold as usize 

 The use of a struct invariant allows us to define (and verify) the possible states that an account can be in at the start and end of an instruction. In this case, our struct invariant rules out the case where 
```
 keys . len () == 0 
```
 and allows us to prove the biconditional 
```
(keys.len() >= 1) -> (instruction succeeds)
```
.

## 4. Safety guarantees 

 Formal verification is an awesome technique, but it is not perfect. There are situations where things are not possible to formally verify, and you need to resort to other methods.

 In particular, one of the difficult-to-verify parts of the Squads Multisig program is cross-program invocation. Specifically, since cross-program invocation executes foreign code, it is difficult (if not impossible) to verify whether this will succeed or fail.

 In the multisig program, this happens in the 
```
 execute_transaction 
```
 instruction.

 So what do you do? 

 For example, in a worst-case scenario you could imagine a situation like the following:

```

```
 1

 #[ derive ( Accounts )] 

 2

 pub MyCtx { 

 3

 #[ account ( mut )] 

 4

 pub my_account : Account < 'info , Acc > 

 5

 } 

 6

 7

 #[ account ] 

 8

 #[ invariant ( bad == false )] 

 9

 struct Acc { 

 10

 pub bad : bool 

 11

 } 

 12

 13

 impl Acc { 

 14

 pub fn put_into_bad_state () { 

 15

 self . bad = true ; 

 16

 } 

 17

 } 

 18

 19

 // Instruction handler: 

 20

 fn hard_to_verify ( ctx : Context < MyCtx >) -> Result <()> { 

 21

 invoke_signed (...); // Cross-program invocation 

 22

 23

 let invoke_res = ...; // fetch result of invocation 

 24

 if invoke_res == 5 { 

 25

 ctx . my_account . put_into_bad_state (); // corrupt our account 

 26

 } 

 27

 Ok (()) 

 28

 } 

```

```

 }#[account]#[invariant(bad == false)]struct Acc { pub bad: bool}impl Acc { pub fn put_into_bad_state() { self.bad = true; }}// Instruction handler:fn hard_to_verify(ctx: Context ) -> Result { invoke_signed(...); // Cross-program invocation let invoke_res = ...; // fetch result of invocation if invoke_res == 5 { ctx.my_account.put_into_bad_state(); // corrupt our account } Ok(())}"> 

 The integrity of the verification framework relies on the fact that the account invariants for the accounts contained in the instruction (in this case 
```
my_account
```
) will be maintained as long as the instruction succeeds.

 In this case, we canât really verify if the instruction succeeds or not (at least without knowing which program/instruction will be invoked).

 However, we can augment our code with additional runtime constraints to ensure that the safety properties are preserved even if formal verification fails.

 In this case, we can add runtime assertions that ensure our runtime invariants hold. For example:

```

```
 1

 ... 

 2

 fn hard_to_verify ( ctx : Context < MyCtx >) -> Result <()> { 

 3

 invoke_signed (...); // Cross-program invocation 

 4

 5

 let invoke_res = ...; // fetch result of invocation 

 6

 if invoke_res == 5 { 

 7

 ctx . my_account . put_into_bad_state (); // corrupt our account 

 8

 } 

 9

 10

 // Enforce invariants at runtime 

 11

 assert ( ctx . my_account . invariant ()); 

 12

 13

 Ok (()) 

 14

 } 

```

```

 ) -> Result { invoke_signed(...); // Cross-program invocation let invoke_res = ...; // fetch result of invocation if invoke_res == 5 { ctx.my_account.put_into_bad_state(); // corrupt our account } // Enforce invariants at runtime assert(ctx.my_account.invariant()); Ok(())}"> 

 Here, we explicitly 
```
 assert 
```
 that our invariants hold at runtime , which allows us to be assured that 
```
my_account
```
 will not enter a bad state as a result of some unverifiable behavior.

 In general, techniques like this can be used to tidy up the loose ends that formal verification may struggle with.

## Challenges of formal verification on Solana 

## Expensive computation 

 As we started exploring this project, we were hoping to see it work straight out of the box. Unfortunately, that was not the case. Harkening back to our friend path explosion , it is often the case that bounded model checking just grinds and grinds on the problem and is not able to produce a solution.

 In order to make this technique more widely applicable, weâve been developing a runtime SDK layer that is more formal verification friendly . Specifically, our tool will replace certain built-in SDK functions and structures with less expensive ones in the context of symbolic execution.

 For example, when verifying things like the uniqueness of a 
```
 Pubkey 
```
 in a 
```
 Vec 
```
, the native program may generate extremely large SMT expressions containing nested 32-byte comparisons and binary searches on a vector.

 However, in most cases the properties we are interested in do not require specific search algorithms for the 
```
 Vec 
```
 or a 32-byte 
```
 Pubkey 
```
. Instead, our tool can substitute in cheaper types and functions, such as a 4-byte 
```
 Pubkey 
```
 struct and a fixed-size, array-backed 
```
 Vec 
```
 implementation. These structures are API-compatible with the native SDK, and the changes are functionally invisible to the Solana program we are verifying. However, the generated expressions are much simpler, and we find that these techniques can greatly accelerate the speed of model checking.

 It is of key importance that these SDK modifications do not introduce any unsoundness into the model-checking process. We are actively exploring how to do this effectively.

## Runtime environment 

 While these techniques are quite capable of verifying pure-Rust constructs such as the logical flow of the program, use of Rust types, etc., other aspects of the Solana runtime environment are more difficult to verify.

 For example, a program may resize accounts to store variable amounts of data. These types of custom serialization algorithms require specialized techniques to verify account invariants. For example, a bug with account serialization could undermine âcorrectâ account logic.

 Another example is cross-program invocation (CPI). While account data cannot be changed by other programs, when you invoke other instructions it becomes more difficult to verify instruction invariants. An instruction three levels down could fail and cause the whole transaction to revert.

## Conclusion 

 Computer security is far from being a solved problem. Formal verification is a great technique, but it is not a magic bullet. While it can help you verify the correctness of your program, it wonât catch 100% of the bugs. It wonât stop you from specifying the wrong invariants or forgetting things, and it canât help you if there is a bug outside of the scope of the model â for example, in the runtime or consensus layer.

 Disclaimer out of the way, we believe that formal verification can still be a very useful tool when applied correctly. Weâve demonstrated that it is possible to automatically prove invariants about Solana programs in a tractable and user-friendly way.

 Note (Get in touch) Weâre excited to keep pushing this research forward and enhance the security of the whole Solana ecosystem. Our tools are still in development, but weâre interested in working with other teams. If you have a Solana program you want to get formally verified, give us a shout! Fill out this form or email us at contact@osec.io .

## Footnotes 

- 
 At least until our AI overlords surpass human intelligence. â©

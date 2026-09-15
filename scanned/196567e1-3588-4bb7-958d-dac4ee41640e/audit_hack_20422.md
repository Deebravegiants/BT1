# [H] OtterSec: The Move Prover: a guide

## Summary
Severity: High
Published: Fri, 16 Sep 2022
Source: https://osec.io/blog/move-prover/
Type: security-research

## Details
## The Move Prover: a guide

 Robert Chen Sep 16, 2022 #move #tutorial A practical guide to the Move Prover â tutorial, case study, and specifications.

## Introduction 

 Formal verification â a powerful tool for proving the correctness of your programs. How does it actually work? This blog post will provide practical tips to help you use the Move Prover to its fullest potential, as well as explore a real-world example of how we used formal verification to secure a smart contract.

 At a high level, formal verification allows you to provide a specification for the program. This specification is then checked against symbolic inputs, allowing you to prove that your code follows the specification for all possible inputs.

## Move Prover 

 The Move Prover is an automated tool that allows developers to formally verify smart contracts written in the Move programming language.

 Move was primarily designed to facilitate automatic verification. Interestingly, the Move Prover operates on the Move bytecode itself, preventing potential compiler bugs from interfering with prover correctness.

 The architecture of the tool consists of multiple components, as illustrated below:

 First, the Move Prover receives a Move source file as input that contains specifications of the intended behavior of the program. Those specifications are then extracted from the annotated source by the Move Parser. Subsequently, the tool compiles the source code into Move bytecode, which is verified and converted into a prover object model plus the specification system âblueprintâ.

 The model is translated into an intermediate language, called Boogie . This Boogie code is then passed to the Boogie verification system, which generates the input for the solver using a âverification condition generationâ. The verification condition (VC) is passed to an automated theorem prover (Z3).

 Once the VC is passed to Z3, the prover checks if the SMT formula is unsatisfiable. If so, it means that the specifications hold. Otherwise, a model that satisfies the conditions is generated and converted back into Boogie format in order to issue a diagnosis report. The diagnosis report is then reverted to a source-level error which parallels a standard compiler error.

## Move Specification Language 

 The Move Specification Language (MSL) is a subset of the Move language, which introduces support for statically describing the correctness of a programâs behavior, with no implications on production.

 To better understand how to use the MSL, we will use Pontemâs U256 library , an open-source Move library which implements support for U256 numbers, as a case study.

 The U256 number is implemented as a struct which contains four 
```
 u64 
```
 numbers:

 u256.move 
```

```
 1

 struct U256 has copy , drop , store { 

 2

 v0: u64 , 

 3

 v1: u64 , 

 4

 v2: u64 , 

 5

 v3: u64 , 

 6

 } 

```

```

 Now, letâs consider the 
```
 add(a: U256, b: U256): U256 
```
 function. In order to verify the correctness of such a function, it might be useful to verify some of the group axioms, for example: commutativity and associativity.

 Specifications are declared in a specification block, which can be found in Move functions, as a module member, or in a different file as a separate specification module. For example, if your file is 
```
sources/u256.move
```
, you can put specifications in sources/u256.spec.move :

```

```
 spec add { ... } 

```

```

 The specifications placed inside the specification blocks are considered expressions .

## Expressions 

 Letâs go over some common expressions.

```
 aborts_if 
```
 defines when the function can abort. This is especially useful in the context of smart contract development, where an abort would cause the entire transaction to roll back.

 For example, the 
```
 add 
```
 function aborts if and only if the U256 addition overflows. Letâs put these words into an expression:

 u256.spec.move 
```

```
 1

 const P64 : u128 = 0x10000000000000000 ; 

 2

 3

 spec fun value_of_U256 ( a : U256 ): num { 

 4

 a.v0 + 

 5

 a.v1 * P64 + 

 6

 a.v2 * P64 * P64 + 

 7

 a.v3 * P64 * P64 * P64 

 8

 } 

 9

 10

 spec add { 

 11

 aborts_if value_of_U256 (a) + value_of_U256 (b) >= P64 * P64 * P64 * P64; 

 12

 } 

```

```

 = P64 * P64 * P64 * P64;}"> 

 We can observe in the snippet above that we are allowed to call functions inside the spec block. However, the callee must either be an MSL function , or a pure Move function. A pure Move function can be defined as a function that does not modify the global state or use Move expression features unsupported by MSL.

 Tip A common pattern for 
```
 aborts_if 
```
 is 
```
 aborts_if false 
```
, which lets you prove that a function will never abort:

```

```
 spec critical_function { 

 aborts_if false ; 

 } 

```

```

 Another type of expression that we can use is 
```
 ensures 
```
. As the name suggests, it ensures that a certain condition is true at the end of a functionâs execution.

 In the case of the 
```
 add 
```
 function, we want to ensure that the return value is the sum of the two parameters. Note that because MSL uses unbounded numbers , weâre able to very cleanly express this property without worrying about overflows:

 u256.spec.move 
```

```
 1

 spec add { 

 2

 aborts_if value_of_U256 (a) + value_of_U256 (b) >= P64 * P64 * P64 * P64; 

 3

 ensures value_of_U256 (result) == value_of_U256 (a) + value_of_U256 (b); 

 4

 } 

```

```

 = P64 * P64 * P64 * P64; ensures value_of_U256(result) == value_of_U256(a) + value_of_U256(b);}"> 

 Note Because Move specification functions are written in MSL, the numbers are unbounded and we can define the expression without risk of overflow.

 Letâs try to prove the library with the specifications from above:

 Terminal window 
```

```
 $ move prove 

```

```

 It outputs the following error information:

```

```
 [...] 

 error: abort not covered by any of the `aborts_if` clauses 

 â­ spec add { 

 | aborts_if value_of_U256(a) + value_of_U256(b) >= P64 * P64 * P64 * P64; 

 | ensures value_of_U256(result) == value_of_U256(a) + value_of_U256(b); 

 | } 

 â°âââââ^ 

 [...] 

 at ./sources/u256.move:316: add 

 enter loop, variable(s) carry, i, ret havocked and reassigned 

 carry = 54 

 i = 3792 

 ret = u256.U256{v0 = 26418, v1 = 27938, v2 = 6900, v3 = 1999} 

 at ./sources/u256.move:346: add 

 ABORTED 

 FAILURE proving 1 modules from package `u256` in 9.143s 

 { 

 "Error": "Move Prover failed: exiting with verification errors" 

 } 

```

```

 = P64 * P64 * P64 * P64;| ensures value_of_U256(result) == value_of_U256(a) + value_of_U256(b);| }â°âââââ^[...] at ./sources/u256.move:316: add enter loop, variable(s) carry, i, ret havocked and reassigned carry = 54 i = 3792 ret = u256.U256{v0 = 26418, v1 = 27938, v2 = 6900, v3 = 1999} at ./sources/u256.move:346: add ABORTEDFAILURE proving 1 modules from package `u256` in 9.143s{ "Error": "Move Prover failed: exiting with verification errors"}"> 

 The prover is telling us that proving failed because the abort was not covered by our 
```
 aborts_if 
```
 clauses. But there is no other abort situation that we have to cover, right?

 If we keep reading the error output, we will encounter the somewhat cryptic message: 
```
ret havocked and reassigned
```
.

 What does this mean?

 By diving into the Move Prover source, we find a likely suspect . The prover attempts to prove all loops with induction!

 More formally, it will translate the loop into two key steps, following the classic steps of a proof by induction:

- Base case : assert that the loop invariant holds at the start of loop execution.

- Inductive step : assume the invariant, execute the loop body, and assert that the invariant still holds.

 The loop prover will also havoc, or assign random values to, all variables written to inside the loop . Going back to the log message, this implies that the variables 
```
 carry 
```
, 
```
 ret 
```
, and 
```
 i 
```
 have been havocked, or assigned random values. This also explains why the input and output of 
```
 add 
```
 make no sense.

 More concretely, the loop analysis translates into the following steps:

- Assert the loop invariant.

- Havoc all modified variables.

- Assume the loop invariant.

- Assume the loop guard (the code inside the 
```
 while 
```
 condition).

- Run the loop body.

- Assert the loop invariant.

 There are two approaches to dealing with loops.

 The first would be to specify a loop invariant. In order to specify the loop invariant, we need to use some special syntax, as we explored briefly in our previous post :

```

```
 1

 while ({ 

 2

 spec { 

 3

 invariant len (amounts_times_coins) == i; 

 4

 invariant i <= n_coins; 

 5

 invariant forall j in 0 ..i: amounts_times_coins[j] == input[j] * n_coins; 

 6

 }; 

 7

 (i < n_coins) 

 8

 }) { 

 9

 vector :: push_back ( 

 10

 & mut amounts_times_coins, 

 11

 (* vector :: borrow (&input, (i as u64 )) as u128 ) * (n_coins as u128 ) 

 12

 ); 

 13

 i = i + 1 ; 

 14

 }; 

```

```

 In this case, the brackets specify the loop invariant for the 
```
 while 
```
 loop. Because the loop invariant executes after the loop guard, we need to account for an extra step with 
```
 i <= n_coins 
```
:

```

```
 1

 while ({ 

 2

 spec { 

 3

 invariant len (amounts_times_coins) == i; 

 4

 invariant i <= n_coins; 

 5

 invariant forall j in 0 ..i: amounts_times_coins[j] == input[j] * n_coins; 

 6

 }; 

 7

 (i < n_coins) 

 8

 }) { 

```

```

 Loop invariants are often difficult to write, especially for nontrivial loop bodies.

 The second solution to dealing with loops is to unroll the loop. This technique works in this particular situation because, as we can observe, the loop within the 
```
 add 
```
 function will always iterate exactly four times:

 u256.move 
```

```
 1

 /// Total words in ` U256 ` (64 * 4 = 256). 

 2

 const WORDS : u64 = 4 ; 

 3

 4

 [...] 

 5

 6

 let i = 0; 

 7

 while (i < WORDS) { 

 8

 let a1 = get (&a, i); 

 9

 let b1 = get (&b, i); 

 10

 11

 [...] 

```

```

 Unrolling the function and running the Move Prover again will print out a success message:

```

```
 SUCCESS proving 1 modules from package `u256` in 9.685s 

 { 

 "Result": "Success" 

 } 

```

```

 For the associative property ( a + ( b + c ) = ( a + b ) + c a + (b + c) = (a + b) + c a + ( b + c ) = ( a + b ) + c ) to be true, changing the grouping of addends should not change the sum. To verify this, we will first implement a function which simulates this property:

```

```
 1

 fun add_assoc_property (a: U256 , b: U256 , c: U256 ): bool { 

 2

 let result_1 = add (b, c); 

 3

 let result_11 = add (a, result_1); 

 4

 let result_2 = add (a, b); 

 5

 let result_22 = add (c, result_2); 

 6

 7

 let cmp = compare (&result_11, &result_22); 

 8

 if ( cmp == EQUAL ) true else false 

 9

 } 

```

```

 Lastly, we want to create a spec block which aborts if the sum overflows, and ensures that the result of the function is true:

```

```
 1

 spec add_assoc_property { 

 2

 aborts_if ( value_of_U256 (a) + value_of_U256 (b)) + value_of_U256 (c) >= P64 * P64 * P64 * P64; 

 3

 ensures result == true ; 

 4

 } 

```

```

 = P64 * P64 * P64 * P64; ensures result == true;}"> 

 Running the Move Prover with the new specifications, we can confirm that there are no verification errors:

```

```
 SUCCESS proving 1 modules from package `u256` in 9.685s 

 { 

 "Result": "Success" 

 } 

```

```

 Tip For a more complete document detailing Move Prover syntax, we recommend referring to spec-lang.md in the Move repository.

## Use cases 

 Formal verification can prove that a smart contract satisfies the given requirements for all possible cases without even running the contract. The hard part is coming up with the specifications.

 Here, we hope to explore some practical examples of possible verification ideas.

## Error conditions 

 Taking an example from 
```
 std::fixed_point32 
```
, itâs often useful to explicitly define when a function might abort. For example, arithmetic operations with fixed-point numbers should only error if they overflow:

 fixed_point32.move 
```

```
 1

 spec schema MultiplyAbortsIf { 

 2

 val: num ; 

 3

 multiplier: FixedPoint32; 

 4

 aborts_if spec_multiply_u64 (val, multiplier) > MAX_U64 with EMULTIPLICATION; 

 5

 } 

 6

 spec fun spec_multiply_u64 ( val : num , multiplier : FixedPoint32 ): num { 

 7

 (val * multiplier.value) >> 32 

 8

 } 

```

```

 MAX_U64 with EMULTIPLICATION;}spec fun spec_multiply_u64(val: num, multiplier: FixedPoint32): num { (val * multiplier.value) >> 32}"> 

## Access control policies 

 Somewhat similar to error conditions, itâs often useful to enforce explicit access control policies at the specification level.

 For example, in 
```
 std::offer 
```
 we are able to see that the function should abort if and only if there does not exist an offer, or the recipient is not allowed:

 offer.move 
```

```
 1

 spec redeem { 

 2

 /// Aborts if there is no offer under ` offer_address ` or if the account 

 3

 /// cannot redeem the offer. 

 4

 /// Ensures that the offered struct under ` offer_address ` is removed. 

 5

 aborts_if !exists<Offer<Offered>>(offer_address); 

 6

 aborts_if ! is_allowed_recipient <Offered>(offer_address, signer:: address_of (account)); 

 7

 ensures !exists<Offer<Offered>>(offer_address); 

 8

 ensures result == old (global<Offer<Offered>>(offer_address).offered); 

 9

 } 

```

```

 >(offer_address); aborts_if !is_allowed_recipient (offer_address, signer::address_of(account)); ensures !exists >(offer_address); ensures result == old(global >(offer_address).offered);}"> 

 These access control specifications make it impossible to accidentally remove security-critical access control policies later.

## Complex mathematical formulae 

 Whether itâs a decimal implementation or more complex data structures, itâs often useful to verify that the expected output is always the output.

 Proving that your fundamental data structures work exactly as intended will give you much more confidence in the remainder of your codebase.

 For example, in our work with Laminar Markets , we provided recommendations for verifying their internal splay tree implementation against a simpler priority queue data structure.

## Data invariants 

 Formal verification provides the best environment to verify that certain 
```
variables
```
 or 
```
resources
```
 donât exceed the intended boundaries. Letâs consider the struct below; we can ensure that 
```
 index 
```
 is never greater than 4 using a 
```
struct invariant
```
:

```

```
 1

 struct Type { 

 2

 index: u64 

 3

 } 

 4

 5

 spec Type { 

 6

 invariant index < 4 ; 

 7

 } 

```

```

 We were able to verify more complex properties in our recent audits for LayerZero and Aries Markets , but the details are left as an exercise to the reader.

## Economic invariants 

 Proper economic invariants can require more creativity to come up with, but can be extremely effective at securing your protocol.

 For example, you should never be able to drain coins from a pool by adding and removing shares. In practice, you might implement this as a utility helper function:

```

```
 1

 // #[test] // TODO: cannot specify the test-only functions 

 2

 fun no_free_money_theorem (coin1_in: u64 , coin2_in: u64 ): ( u64 , u64 ) acquires Pool { 

 3

 let share = add_liquidity (coin1_in, coin2_in); 

 4

 remove_liquidity (share) 

 5

 } 

 6

 spec no_free_money_theorem { 

 7

 pragma verify= false ; 

 8

 ensures result_1 <= coin1_in; 

 9

 ensures result_2 <= coin2_in; 

 10

 } 

```

```

 Some other ideas include:

- Swapping through an AMM should never lead to a decrease in one side of the pool without also increasing the other side. In other words, no free money.

- Lending protocols should always be fully collateralized after a series of deposit, borrow, and withdraw instructions.

- Orderbooks should never lose money after an order is placed and then canceled.

## Closing thoughts 

 In this post, weâve explored how to properly utilize the Move Prover to verify critical invariants about your codebase.

 In our upcoming posts, we will explore how to turn the Move Prover into a weapon for squashing security vulnerabilities by learning how to ask the right questions, so stay tuned!

 Weâre passionate about formal verification and pushing the edge of whatâs possible in Move security. If you have any thoughts, or would like to explore an audit, feel free to reach out to me @notdeghost .

# [M] OtterSec: Move: an auditor’s introduction

## Summary
Severity: Medium
Published: Tue, 06 Sep 2022
Source: https://osec.io/blog/move-introduction/
Type: security-research

## Details
## Move: an auditorâs introduction

 Robert Chen Sep 6, 2022 What actually makes Move secure? A discussion of Moveâs typing system and formal verification.

## Introduction 

 As part of our work, we seek to understand how to eliminate vulnerability classes. Designing safer languages enables developers to write code with confidence. How exactly does Move lend itself to safer programming practices? What can we learn from Move to generalize secure design principles for other execution environments?

 Lately, there appear to be many buzzwords floating around: formal verification, type-based safety, ârust but for blockchainâ.

 In this piece Iâll seek to discuss exactly how Move lends itself to more secure programming practices, potential shortcomings, and practical design tips for protocol developers looking to build structurally safer programs.

## Types 

 One of the key selling points of Move is the use of typed resources. Aptos and Sui have slight variations in how they materialize this pattern, but as an example, take 
```
coin.move
```
:

 coin.move (Aptos) 
```

```
 1

 /// Main structure representing a coin/token in an account's custody. 

 2

 struct Coin < phantom CoinType > has store { 

 3

 /// Amount of coin this address has. 

 4

 value: u64 , 

 5

 } 

```

```

 has store { /// Amount of coin this address has. value: u64,}"> 

 coin.move (Sui) 
```

```
 1

 /// A coin of type ` T ` worth ` value `. Transferable and storable 

 2

 struct Coin < phantom T > has key , store { 

 3

 id: UID , 

 4

 balance: Balance < T > 

 5

 } 

```

```

 has key, store { id: UID, balance: Balance }"> 

 Pulling an example from Pontem Networkâs Liquidswap DEX implementation on Aptos, we can see that 
```
 LiquidityPool 
```
 natively embeds this type information into its fields:

 liquidity_pool.move 
```

```
 1

 /// Liquidity pool with reserves. 

 2

 struct LiquidityPool < phantom X , phantom Y , phantom LP > has key { 

 3

 coin_x_reserve: Coin < X >, 

 4

 coin_y_reserve: Coin < Y >, 

 5

 // ... 

 6

 } 

```

```

 has key { coin_x_reserve: Coin , coin_y_reserve: Coin , // ...}"> 

 This has the advantage of aligning type information at compile time. It would be difficult to accidentally pass in the wrong type of coin to a function:

 liquidity_pool.move 
```

```
 1

 public fun mint < X , Y , LP >( 

 2

 pool_addr: address , 

 3

 coin_x: Coin < X >, 

 4

 coin_y: Coin < Y > 

 5

 ): Coin < LP > acquires LiquidityPool , EventsStore { 

 6

 // ... 

 7

 8

 let (x_reserve_size, y_reserve_size) = get_reserves_size < X , Y , LP >(pool_addr); 

```

```

 ( pool_addr: address, coin_x: Coin , coin_y: Coin ): Coin acquires LiquidityPool, EventsStore { // ... let (x_reserve_size, y_reserve_size) = get_reserves_size (pool_addr);"> 

 Note (Generics at the VM level) This generic type information is implemented at runtime in the 
```
 ty_args 
```
 at the VM level . This VM-level implementation choice makes it rather difficult to iterate over arbitrary generic types, such as with summing the coins in a pool. We will be releasing a deep dive into Moveâs VM internals shortly.

 In pseudocode, this checks that 
```
coin_x.type
```
 is equal to 
```
pool.x_type
```
, and 
```
coin_y.type
```
 is equal to 
```
pool.y_type
```
.

 This type system has two advantages:

- Itâs required. The type parameter must be specified, so itâs impossible to forget such a constraint.

- Itâs concise. Constraints are done via type parameter alignment instead of verbose equivalence checks.

 However, this system isnât perfect.

 In fact, I would go as far as to argue that using types to create such associations is an anti-pattern .

 Using types to enforce relationships only works because types are uniquely associated with instances. For example, in Aptosâs coin initialization function, they explicitly assert that there hasnât been a previously initialized 
```
 CoinInfo<CoinType> 
```
:

 coin.move 
```

```
 1

 fun initialize_internal < CoinType >( 

 2

 // ... 

 3

 ): ( BurnCapability < CoinType >, FreezeCapability < CoinType >, MintCapability < CoinType >) { 

 4

 // ... 

 5

 6

 assert! ( 

 7

 ! exists < CoinInfo < CoinType >>(account_addr), 

 8

 error:: already_exists ( ECOIN_INFO_ALREADY_PUBLISHED ), 

 9

 ); 

```

```

 ( // ...): (BurnCapability , FreezeCapability , MintCapability ) { // ... assert!( !exists >(account_addr), error::already_exists(ECOIN_INFO_ALREADY_PUBLISHED), );"> 

 While this 
```
 CoinInfo 
```
 isnât returned directly, it still ensures uniqueness of the capability objects.

 Similarly, consider Aries Markets , a lending/borrowing protocol building on Aptos.

 Their 
```
 ReserveCoinContainer 
```
 struct stores all the relevant data and resources for managing a lending market:

```

```
 1

 /// The struct to hold all the underlying ` Coin `s. 

 2

 /// Stored as a resources. 

 3

 struct ReserveCoinContainer < phantom Coin0 > has key { 

 4

 /// Stores the available ` Coin `. 

 5

 underlying_coin: Coin < Coin0 >, 

 6

 /// Stores the LP ` Coin ` that act as collateral. 

 7

 collateralised_lp_coin: Coin < LP < Coin0 >>, 

 8

 /// Mint capability for LP Coin. 

 9

 mint_capability: MintCapability < LP < Coin0 >>, 

 10

 /// Burn capability for LP Coin. 

 11

 burn_capability: BurnCapability < LP < Coin0 >>, 

 12

 13

 // ... 

 14

 } 

```

```

 has key { /// Stores the available `Coin`. underlying_coin: Coin , /// Stores the LP `Coin` that act as collateral. collateralised_lp_coin: Coin >, /// Mint capability for LP Coin. mint_capability: MintCapability >, /// Burn capability for LP Coin. burn_capability: BurnCapability >, // ...}"> 

 When creating a 
```
 ReserveCoinContainer 
```
, uniqueness is implicitly enforced by moving it into a hardcoded address:

```

```
 1

 public ( friend ) fun create < Coin0 >( 

 2

 lp_store: & signer , 

 3

 // ... 

 4

 ) acquires Reserves { 

 5

 lp:: assert_is_lp_store ( signer :: address_of (lp_store)); 

 6

 7

 // ... 

 8

 9

 move_to (lp_store, ReserveCoinContainer < Coin0 > { 

 10

 // ... 

 11

 }); 

```

```

 ( lp_store: &signer, // ...) acquires Reserves { lp::assert_is_lp_store(signer::address_of(lp_store)); // ... move_to(lp_store, ReserveCoinContainer { // ... });"> 

 In both these instances, type association only works because we create exactly one instance per type.

 On the other hand, consider if you have a 
```
 Position<T> 
```
 and a 
```
 Market<T> 
```
 where 
```
T
```
 is the coin type:

```

```
 1

 struct Market < phantom T > { 

 2

 reserves: Coin < T >, 

 3

 // ... 

 4

 } 

 5

 6

 struct Position < phantom T > { 

 7

 amount: u64 , 

 8

 // ... 

 9

 } 

```

```

 { reserves: Coin , // ...}struct Position { amount: u64, // ...}"> 

 If 
```
 Market<T> 
```
 isnât a unique type â or, in other words, if youâre able to create more than one instance of a market per type 
```
T
```
 â you might be able to pass in the incorrect market for a given position. This is a common vulnerability pattern on Solana.

 Dynamic iteration of types is also impossible (at least as currently designed by the Move VM), leading to massive headaches for developers. In these scenarios, we empirically observe developers defaulting back to type reflection APIs, complicating code unnecessarily:

```

```
 1

 /// Get the price of the token per lamport. 

 2

 public fun get_price (type_info: TypeInfo ): Decimal acquires Oracle { 

 3

 let oracle = borrow_global_mut < Oracle >( @oracle ); 

 4

 let price = table:: borrow_mut_with_default < TypeInfo , Decimal >( 

 5

 & mut oracle.prices, 

 6

 type_info, 

 7

 decimal:: one () 

 8

 ); 

 9

 *price 

 10

 } 

```

```

 (@oracle); let price = table::borrow_mut_with_default ( &mut oracle.prices, type_info, decimal::one() ); *price}"> 

 Security at the expense of usability comes at the expense of security.

 Type association feels like a proxy for the intended pattern â associating resources with instances. Itâs very useful being able to store a reference to an instance of another resource (which is possible in Diem-style Move).

 In summary, when using type systems to bind resources to each other, itâs important to either:

- Have unique initializers for your resources.

- Associate resources with instances directly.

## Formal verification 

 Formal verification is another exciting feature.

 As part of our work with protocols, we actively use formal verification to prove aspects of security.

 However, this isnât a silver bullet. The key is figuring out what to prove.

 One obvious idea might be a property across a particular function. For example, we might want to ensure that a swap doesnât reduce the value of the pool â similar to the Solana AMM rounding issue we reported.

 However, this could also be checked with a simple runtime assert. For example, we recommended Pontem assert that liquidity pool token values are strictly increasing:

```

```
 let cmp = u256::compare(&lp_value_after_swap_and_fee, &lp_value_before_swap_u256); 

 assert!(cmp == 2, ERR_INCORRECT_SWAP); 

```

```

 The Move Prover really shines when weâre proving relationships between functions.

 One example of a more complicated relationship that canât be proved easily via assertions would be the 
```
 no_free_money_theorem 
```
 in the Move repository:

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

 Thereâs no clean way to express this with an assert because this makes an observation across two functions which are temporally separated.

 Invariants are also extremely useful. For example, enforcing invariants about fee parameters (fee can never be greater than 100%) or pool supply makes it a lot easier to reason about the protocol.

 For example, Ian uses invariants to clearly define core properties of his AMM state:

```

```
 spec PoolState { 

 invariant supply >= MINIMUM_LIQUIDITY; 

 } 

```

```

 = MINIMUM_LIQUIDITY;}"> 

 Another useful pattern for the Move Prover is 
```
 aborts_if 
```
. More specifically, it can be very helpful to assert that a function never aborts, with 
```
 aborts_if false 
```
.

 Although loop invariants are a bit clunky, Ian is also able to prove that a relatively nontrivial function doesnât abort:

```

```
 1

 fun multiply_vec_by_n_coins (input: vector < u64 >): vector < u128 > { 

 2

 let amounts_times_coins = vector :: empty < u128 >(); 

 3

 let i = 0 ; 

 4

 let n_coins = vector :: length (&input); 

 5

 while ({ 

 6

 spec { 

 7

 invariant len (amounts_times_coins) == i; 

 8

 invariant i <= n_coins; 

 9

 invariant forall j in 0 ..i: amounts_times_coins[j] == input[j] * n_coins; 

 10

 }; 

 11

 (i < n_coins) 

 12

 }) { 

 13

 vector :: push_back ( 

 14

 & mut amounts_times_coins, 

 15

 (* vector :: borrow (&input, (i as u64 )) as u128 ) * (n_coins as u128 ) 

 16

 ); 

 17

 i = i + 1 ; 

 18

 }; 

 19

 spec { 

 20

 assert i == n_coins; 

 21

 assert len (input) == n_coins; 

 22

 }; 

 23

 amounts_times_coins 

 24

 } 

 25

 spec multiply_vec_by_n_coins { 

 26

 pragma opaque; 

 27

 aborts_if false ; 

 28

 ensures len (result) == len (input); 

 29

 ensures forall j in 0 .. len (input): result[j] == input[j] * len (input); 

 30

 } 

```

```

 ): vector { let amounts_times_coins = vector::empty (); let i = 0; let n_coins = vector::length(&input); while ({ spec { invariant len(amounts_times_coins) == i; invariant i 

## Closing thoughts 

 In this post, we explored implications of Moveâs type system and formal verification, two powerful features of the Move language that enable safer programming practices.

 While Move is still a language in active development, it shows some exciting features that seem to allow developers to create structurally safer programs.

 Weâre passionate about pushing the edge of whatâs possible in Move security. If you have any thoughts, or would like to explore an audit, feel free to reach out to me @notdeghost .

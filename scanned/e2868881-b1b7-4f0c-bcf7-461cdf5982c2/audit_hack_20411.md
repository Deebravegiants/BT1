# [H] OtterSec: Auto reverse-engineering the Hyperliquid risk engine, with some agentic help

## Summary
Severity: High
Published: Mon, 22 Jun 2026
Source: https://osec.io/blog/hyperliquid-risk-engine/
Type: security-research

## Details
## Auto reverse-engineering the Hyperliquid risk engine, with some agentic help

 Renato Marziano Jun 22, 2026 #hyperliquid #reverse-engineering #defi Perps allow traders to leverage beyond their collateral, until the market turns abruptly and losses are clawed back. We auto-reverse engineer Hyperliquidâs risk engine to show how it ranks and deleverages winning users under the solvencyâfairnessârevenue trilemma.

## Perpetuals 

 Definition A perpetual is a bet on a price, usually leveraged, settled in stablecoins, and with no expiry. It is a row in the exchangeâs ledger, backed by margin, where one sideâs gains are the other sideâs losses on the same book.

 What does that even have to do with reverse engineering?

## Hyperliquid 

 Hyperliquid is a decentralized perpetuals exchange. It runs on its own L1, released publicly for anybody to run, but closed source. The order book and the risk engine live on-chain, and thus inside of the L1 node binary, sitting between users and the shared balance sheet theyâre all betting against.

 The node has a very hard problem . It must keep the books balanced when leverage makes it possible for one side of every trade to lose more than their margin covers.

 Implementing a correct algorithm that solves this question is exactly what keeps the exchange solvent. This is also why peering into the actual implementation is very intriguing from a security standpoint.

 Beyond that, the 
```
hl-node
```
 binary also offers an additional technical thrill. It is written in Rust, which is notoriously hard to reverse engineer.

 Armed with some curiosity, a good amount of inference , and the right tooling, weâll take a deep dive into the reconstructed code so that anybody can follow along, while also giving reverse engineers something to learn.

## The million dollar question 

 Letâs say a terrible trader opens a 50x leveraged position on Hyperliquid. How does the exchange avoid losing money from their eventual downfall?

 When the market turns against them, the first check they would encounter is the traditional liquidation. Their position is automatically put up on the market on the opposite side of the book. This happens whenever the equity of the position drops below the maintenance margin, which is spelled out exactly in the 
```
 compute_margin_requirement_by_mode () 
```
 function.

 Start with the simplest case, an isolated position. The relevant function is 
```
 compute_account_value_for_direction () 
```
.

```
 compute_account_value_for_direction () 
```
 
```

```
 int64_t sub_555556bb4d20 ( int64_t arg1 , int64_t arg2 , int64_t arg3 , int64_t arg4 , int64_t arg5 , int64_t arg6 ) 

 struct OptionUnitQty * compute_account_value_for_direction ( struct OptionUnitQty * result , struct UserState * user_state , uint8_t is_isolated , uint64_t asset_idx , uint32_t margin_mode , void * oracle_data ) 

```

```

 The important part is the argument list. The function receives a 
```
 UserState 
```
, an isolated or cross selector, an asset index, a margin mode, and oracle data.

 The body splits on 
```
 is_isolated 
```
. Cross margin takes the account-wide path, while isolated margin continues into the single-position calculation.

```
 compute_account_value_for_direction () 
```
 
```

```
 struct OptionUnitQty * compute_account_value_for_direction ( struct OptionUnitQty * result , struct UserState * user_state , uint8_t is_isolated , uint64_t asset_idx , uint32_t margin_mode , void * oracle_data ) 

 { 

 4 collapsed lines 

 int128_t var_138 ; 

 struct OptionUnitQty lhs ; 

 int64_t rax , rcx , rdx ; 

 bool cond ; 

 if (!( is_isolated & 1 )) 

 { 

 // Cross margin computes account-wide value and shortfall. 

 compute_user_margin_and_shortfall (& var_138 , user_state , oracle_data , nullptr ); 

 return result ; 

 } 

 // Isolated margin uses this asset's margin and own PnL. 

 } 

```

```

 The important detail is that isolated equity is local to the position. It is the isolated margin plus the positionâs own PnL. From there the threshold reduces to this expression.

 liq_equity = â£ notional â£ 2 â leverage \text{liq\_equity} = \frac{|\text{notional}|}{2 \cdot \text{leverage}} liq_equity = 2 â leverage â£ notional â£ â 

## What if nobody wants to buy the position? 

 The market order from the previous section is just a regular order, and it still needs somebody on the other side of the book to fill it. If the book is thin or the move was violent enough that every passive bid got swept, only part of it (or none) gets filled and equity will possibly keep on going down.

 When that happens, the exchange is basically left with a hot potato to get rid of. What should it even do with the debt?

## The risk engine 

 And now we circle back to the risk engine. In order to keep all of these terrible traders from driving the system into ruin, we need some automatic way to prevent and clear bad debt.

 The Hyperliquid docs explain that positions below 2/3 maintenance margin are backstop-liquidated into the HLP liquidator vault. When even that canât keep the book solvent, auto-deleveraging closes the position against opposing traders. What does that even mean?

 To get a better idea of whatâs going on here, we turn to the binary itself and trace the actual logic. A simple testnet sync gives us a lot of context. Within the nodeâs ABCI state, we can see a pretty complex structure named 
```
Clearinghouse
```
 , a struct containing all liquidation-related info, nested within a bigger 
```
 Exchange 
```
 data structure. This is an example of what it might hold when serialized as 
```
MessagePack
```
 at runtime ( download the sample dump , 234 MB).

 This data will come in handy both for us and the agent.

 Now, when does the risk engine actually check positions? We can answer that question by playing around with xrefs starting from the known field strings in 
```
 Clearinghouse 
```
. Some renaming later, the call path looks like this:

 exchange_end_block calls clearinghouse_adl_orchestrator at the end of every block. Call path into the ADL orchestrator exchange_end_block calls clearinghouse_adl_orchestrator at the end of every block. 

```
 exchange_end_block () 
```

```
 clearinghouse_adl_orchestrator () 
```

 - 
 We have one huge function handling all clearinghouse operations, which we call 
```
 clearinghouse_adl_orchestrator () 
```
. It is invoked at the end of each block by a top-level method (called indirectly elsewhere, most likely a trait method) that we call 
```
 exchange_end_block () 
```
. So, at the end of each block we run some checks.

 Take the 
```
 only_isolated 
```
 branch, which fast-tracks certain assets straight to deleveraging:

 1 Â· Raw decompiler 2 Â· Named & typed 3 Â· Idiomatic Rust 

```

```
 int64_t var_28 = *( arg1 + 8 ); 

 if (*( arg2 + ( var_28 << 5 ) + 0x18 ) != 0 ) { 

 if ( LOGGER_ONCE_CELL != 3 ) 

 once_cell_get_or_init (& LOGGER_ONCE_CELL , 0 , & var_a0 , & data_55555878bb08 ); 

 int64_t rax_11 = rust_alloc ( 0x34 ); 

 __builtin_strncpy ( rax_11 , "immediately auto-deleveraging only_isolated position" , 0x34 ); 

 // ...append entry... 

 } 

```

```

```

```
 int64_t entry_asset_idx = *( ph1_entry_ptr + 8 ); 

 if ( clearinghouse -> asset_count <= entry_asset_idx ) 

 panic_index_out_of_bounds ( entry_asset_idx , clearinghouse -> asset_count ); 

 if (*( clearinghouse -> asset_array_ptr + ( entry_asset_idx << 5 ) + 0x18 )) // asset.strict_isolated != 0 

 { 

 if ( LOGGER_ONCE_CELL != 3 ) 

 once_cell_get_or_init (& LOGGER_ONCE_CELL , 0 , & scratch_opt , & data_55555878bb08 ); 

 int64_t rax_11 = rust_alloc ( 0x34 ); 

 __builtin_strncpy ( rax_11 , "immediately auto-deleveraging only_isolated position" , 0x34 ); 

 // ...append to the deferred queue... 

 } 

```

```

 asset_count asset_count);if (*(clearinghouse->asset_array_ptr + (entry_asset_idx 

```

```
 if asset_strict_isolated ( ch , * asset_idx ) { 

 fill_ctx . log_lines . push ( String :: from ( "immediately auto-deleveraging only_isolated position" )); 

 deferred_cross_queue . push ((* counterparty_addr , * asset_idx )); 

 } 

```

```

 This branch gives us the first ADL shortcut. Strict isolated assets bypass the normal aggregate-shortfall gate and go straight into the ADL queue.

 From there, the ADL path has a clean four-phase shape:

```
 clearinghouse_adl_orchestrator () 
```
 
```

```

 98 collapsed lines 

 1

 use std :: collections ::{ BTreeMap , HashMap }; 

 2

 3

 pub struct OptionUnitQty { 

 4

 pub tag : u64 , 

 5

 pub unit : u64 , 

 6

 pub value : i64 , 

 7

 } 

 8

 9

 pub struct UserState { 

 10

 pub acct_value : OptionUnitQty , 

 11

 pub margin_used : OptionUnitQty , 

 12

 pub positions : BTreeMap < u64 , [ u64 ; 17 ]>, 

 13

 pub funding_state : OptionUnitQty , 

 14

 } 

 15

 16

 pub struct AssetConfig { 

 17

 pub coin : String , 

 18

 pub strict_isolated : bool , 

 19

 pub spot_only : bool , 

 20

 pub max_leverage : u16 , 

 21

 pub asset_flags : u32 , 

 22

 } 

 23

 24

 pub struct OraclePrice { 

 25

 pub mark : u64 , 

 26

 pub oracle : u64 , 

 27

 pub mid : u64 , 

 28

 pub funding_rate : u64 , 

 29

 pub spot : u64 , 

 30

 pub last_trade : u64 , 

 31

 pub min_size : u64 , 

 32

 pub tick_size : u64 , 

 33

 pub szi : u64 , 

 34

 pub usd_value : u64 , 

 35

 pub interest : u64 , 

 36

 pub volume : u64 , 

 37

 } 

 38

 39

 pub struct OracleData { 

 40

 pub prices : Vec < OraclePrice >, 

 41

 pub recent_oi : BTreeMap < u64 , OptionUnitQty >, 

 42

 } 

 43

 44

 pub struct AdlFillTracker { 

 45

 pub log_lines : Vec < String >, 

 46

 pub pending_fills : Vec < u64 >, 

 47

 pub fill_list_idx : u64 , 

 48

 pub asset_to_fills : String , 

 49

 pub block_time_us : u64 , 

 50

 } 

 51

 52

 pub struct Clearinghouse { 

 53

 pub total_net_deposit : OptionUnitQty , 

 54

 pub total_non_bridge_deposit : OptionUnitQty , 

 55

 pub adl_shortfall_remaining : OptionUnitQty , 

 56

 pub bridge2_withdraw_fee : OptionUnitQty , 

 57

 pub default_user_state : UserState , 

 58

 pub lookup_asset_ref : u64 , 

 59

 pub assets : & 'static [ AssetConfig ], 

 60

 pub oracle_prices : Vec < OraclePrice >, 

 61

 pub oracle_funding : OptionUnitQty , 

 62

 pub oracle_misc : OptionUnitQty , 

 63

 pub margin_tables : BTreeMap < u64 , u64 >, 

 64

 pub user_states : BTreeMap <[ u8 ; 20 ], UserState >, 

 65

 pub vault_states : HashMap <[ u8 ; 20 ], u64 >, 

 66

 pub spot_balances : HashMap <[ u8 ; 20 ], u64 >, 

 67

 pub spot_meta : HashMap < u64 , u64 >, 

 68

 pub builder_fees : BTreeMap < u64 , u64 >, 

 69

 pub asset_recent_oi : BTreeMap < u64 , u64 >, 

 70

 pub perform_auto_deleveraging : bool , 

 71

 } 

 72

 73

 fn ouq_value ( quote : & OptionUnitQty ) -> i64 { quote . value } 

 74

 75

 fn account_value_for_direction ( _user : & UserState , _asset_idx : u64 , _oracle : & OracleData ) -> OptionUnitQty { 

 76

 OptionUnitQty { tag : 0 , unit : 0 , value : 0 } 

 77

 } 

 78

 79

 fn margin_and_shortfall ( _user : & UserState , _oracle : & OracleData ) -> OptionUnitQty { 

 80

 OptionUnitQty { tag : 0 , unit : 0 , value : 0 } 

 81

 } 

 82

 83

 fn build_counterparty_fills ( _ch : & Clearinghouse , _ctx : & mut AdlFillTracker , _oracle : & mut OracleData , _addr : &[ u8 ; 20 ], _asset_idx : u64 ) -> Vec < u8 > { 

 84

 Vec :: new () 

 85

 } 

 86

 87

 fn process_counterparty_fill ( _ch : & Clearinghouse , _ctx : & mut AdlFillTracker , _oracle : & mut OracleData , _asset_idx : u64 , _direction : u8 , _byte : u8 ) -> i64 { 

 88

 0 

 89

 } 

 90

 91

 fn lookup_user_state < 'a >( ch : & 'a Clearinghouse , counterparty_addr : &[ u8 ; 20 ]) -> & 'a UserState { 

 92

 ch . user_states . get ( counterparty_addr ). unwrap_or (& ch . default_user_state ) 

 93

 } 

 94

 95

 fn asset_strict_isolated ( ch : & Clearinghouse , asset_idx : u64 ) -> bool { 

 96

 ch . assets . get ( asset_idx as usize ). map (| a | a . strict_isolated ). unwrap_or ( false ) 

 97

 } 

 98

 99

 pub fn clearinghouse_adl_orchestrator ( ch : & Clearinghouse , fill_ctx : & mut AdlFillTracker , oracle : & mut OracleData , candidates : & BTreeMap <[ u8 ; 20 ], u64 >) -> BTreeMap <( u64 , u8 ), Vec < u8 >> { 

 100

 let mut result : BTreeMap <( u64 , u8 ), Vec < u8 >> = BTreeMap :: new (); 

 101

 let mut total_shortfall_value : i64 = 0 ; 

 102

 let mut deferred_cross_queue : Vec <([ u8 ; 20 ], u64 )> = Vec :: new (); 

 103

 104

 let mut pointer = candidates . iter (); 

 105

 while let Some (( counterparty_addr , asset_idx )) = pointer . next () { 

 106

 let user_state = lookup_user_state ( ch , counterparty_addr ); 

 107

 let user_shortfall = account_value_for_direction ( user_state , * asset_idx , oracle ); 

 108

 let value = ouq_value (& user_shortfall ); 

 109

 if value > 0 { 

 110

 panic! ( "Bug! ADL candidate account value was not negative" ); 

 111

 } 

 112

 if asset_strict_isolated ( ch , * asset_idx ) { 

 113

 fill_ctx . log_lines . push ( String :: from ( "immediately auto-deleveraging only_isolated position" )); 

 114

 deferred_cross_queue . push ((* counterparty_addr , * asset_idx )); 

 115

 } else { 

 116

 total_shortfall_value = total_shortfall_value . wrapping_sub ( value ); 

 117

 } 

 118

 } 

 119

 120

 let remaining_shortfall = ch . adl_shortfall_remaining . value ; 

 121

 let adl_was_triggered = total_shortfall_value >= remaining_shortfall ; 

 122

 if adl_was_triggered { 

 123

 deferred_cross_queue . clear (); 

 124

 let mut pointer_1 = candidates . iter (); 

 125

 while let Some (( counterparty_addr , asset_idx )) = pointer_1 . next () { 

 126

 deferred_cross_queue . push ((* counterparty_addr , * asset_idx )); 

 127

 } 

 128

 } 

 129

 130

 let mut counterparty_array : Vec <[ u8 ; 20 ]> = Vec :: new (); 

 131

 let mut pointer_2 = deferred_cross_queue . iter (); 

 132

 while let Some (&( counterparty_addr , asset_idx )) = pointer_2 . next () { 

 133

 let user_state = lookup_user_state ( ch , & counterparty_addr ); 

 134

 let cpty_abs_position = margin_and_shortfall ( user_state , oracle ); 

 135

 let _ = cpty_abs_position ; 

 136

 counterparty_array . push ( counterparty_addr ); 

 137

 let counterparty_info = build_counterparty_fills ( ch , fill_ctx , oracle , & counterparty_addr , asset_idx ); 

 138

 result . insert (( asset_idx , 0 u8 ), counterparty_info ); 

 139

 } 

 140

 let counterparty_count = counterparty_array . len (); 

 141

 let _ = counterparty_count ; 

 142

 143

 let mut pointer_3 = result . iter_mut (); 

 144

 while let Some ((&( asset_idx , expected_kind ), counterparty_info )) = pointer_3 . next () { 

 145

 let length = counterparty_info . len (); 

 146

 let mut i : usize = 0 ; 

 147

 while i < length { 

 148

 let cpty_addr_bytes = counterparty_info [ i ]; 

 149

 let fill_delta = process_counterparty_fill ( ch , fill_ctx , oracle , asset_idx , expected_kind , cpty_addr_bytes ); 

 150

 let _ = fill_delta ; 

 151

 i = i . wrapping_add ( 1 ); 

 152

 } 

 153

 } 

 154

 155

 if ! ch . perform_auto_deleveraging { 

 156

 result . clear (); 

 157

 } 

 158

 result 

 159

 } 

```

```

 , pub funding_state: OptionUnitQty,}pub struct AssetConfig { pub coin: String, pub strict_isolated: bool, pub spot_only: bool, pub max_leverage: u16, pub asset_flags: u32,}pub struct OraclePrice { pub mark: u64, pub oracle: u64, pub mid: u64, pub funding_rate: u64, pub spot: u64, pub last_trade: u64, pub min_size: u64, pub tick_size: u64, pub szi: u64, pub usd_value: u64, pub interest: u64, pub volume: u64,}pub struct OracleData { pub prices: Vec , pub recent_oi: BTreeMap ,}pub struct AdlFillTracker { pub log_lines: Vec , pub pending_fills: Vec , pub fill_list_idx: u64, pub asset_to_fills: String, pub block_time_us: u64,}pub struct Clearinghouse { pub total_net_deposit: OptionUnitQty, pub total_non_bridge_deposit: OptionUnitQty, pub adl_shortfall_remaining: OptionUnitQty, pub bridge2_withdraw_fee: OptionUnitQty, pub default_user_state: UserState, pub lookup_asset_ref: u64, pub assets: &'static [AssetConfig], pub oracle_prices: Vec , pub oracle_funding: OptionUnitQty, pub oracle_misc: OptionUnitQty, pub margin_tables: BTreeMap , pub user_states: BTreeMap , pub vault_states: HashMap , pub spot_balances: HashMap , pub spot_meta: HashMap , pub builder_fees: BTreeMap , pub asset_recent_oi: BTreeMap , pub perform_auto_deleveraging: bool,}fn ouq_value(quote: &OptionUnitQty) -> i64 { quote.value }fn account_value_for_direction(_user: &UserState, _asset_idx: u64, _oracle: &OracleData) -> OptionUnitQty { OptionUnitQty { tag: 0, unit: 0, value: 0 }}fn margin_and_shortfall(_user: &UserState, _oracle: &OracleData) -> OptionUnitQty { OptionUnitQty { tag: 0, unit: 0, value: 0 }}fn build_counterparty_fills(_ch: &Clearinghouse, _ctx: &mut AdlFillTracker, _oracle: &mut OracleData, _addr: &[u8; 20], _asset_idx: u64) -> Vec { Vec::new()}fn process_counterparty_fill(_ch: &Clearinghouse, _ctx: &mut AdlFillTracker, _oracle: &mut OracleData, _asset_idx: u64, _direction: u8, _byte: u8) -> i64 { 0}fn lookup_user_state (ch: &'a Clearinghouse, counterparty_addr: &[u8; 20]) -> &'a UserState { ch.user_states.get(counterparty_addr).unwrap_or(&ch.default_user_state)}fn asset_strict_isolated(ch: &Clearinghouse, asset_idx: u64) -> bool { ch.assets.get(asset_idx as usize).map(|a| a.strict_isolated).unwrap_or(false)}pub fn clearinghouse_adl_orchestrator(ch: &Clearinghouse, fill_ctx: &mut AdlFillTracker, oracle: &mut OracleData, candidates: &BTreeMap ) -> BTreeMap > { let mut result: BTreeMap > = BTreeMap::new(); let mut total_shortfall_value: i64 = 0; let mut deferred_cross_queue: Vec = Vec::new(); let mut pointer = candidates.iter(); while let Some((counterparty_addr, asset_idx)) = pointer.next() { let user_state = lookup_user_state(ch, counterparty_addr); let user_shortfall = account_value_for_direction(user_state, *asset_idx, oracle); let value = ouq_value(&user_shortfall); if value > 0 { panic!("Bug! ADL candidate account value was not negative"); } if asset_strict_isolated(ch, *asset_idx) { fill_ctx.log_lines.push(String::from("immediately auto-deleveraging only_isolated position")); deferred_cross_queue.push((*counterparty_addr, *asset_idx)); } else { total_shortfall_value = total_shortfall_value.wrapping_sub(value); } } let remaining_shortfall = ch.adl_shortfall_remaining.value; let adl_was_triggered = total_shortfall_value >= remaining_shortfall; if adl_was_triggered { deferred_cross_queue.clear(); let mut pointer_1 = candidates.iter(); while let Some((counterparty_addr, asset_idx)) = pointer_1.next() { deferred_cross_queue.push((*counterparty_addr, *asset_idx)); } } let mut counterparty_array: Vec = Vec::new(); let mut pointer_2 = deferred_cross_queue.iter(); while let Some(&(counterparty_addr, asset_idx)) = pointer_2.next() { let user_state = lookup_user_state(ch, &counterparty_addr); let cpty_abs_position = margin_and_shortfall(user_state, oracle); let _ = cpty_abs_position; counterparty_array.push(counterparty_addr); let counterparty_info = build_counterparty_fills(ch, fill_ctx, oracle, &counterparty_addr, asset_idx); result.insert((asset_idx, 0u8), counterparty_info); } let counterparty_count = counterparty_array.len(); let _ = counterparty_count; let mut pointer_3 = result.iter_mut(); while let Some((&(asset_idx, expected_kind), counterparty_info)) = pointer_3.next() { let length = counterparty_info.len(); let mut i: usize = 0; while i 

 ADL is meant as an emergency measure. Unlike liquidations, it is not always operational. In this view, the flag appears as a final guard. Unless 
```
 clearinghouse . perform_auto_deleveraging 
```
 is set, the result is cleared before returning.

```
 clearinghouse_adl_orchestrator () 
```
 
```

```
 155

 if ! ch . perform_auto_deleveraging { 

 156

 result . clear (); 

 157

 } 

 158

 result 

 159

 } 

```

```

 Note (Execution gate) The lower-level decompilation is more precise here. In the binary view, 
```
 perform_auto_deleveraging 
```
 gates the actual forced-close call inside Phase 4.

```

```
 if (! clearinghouse_1 -> perform_auto_deleveraging ) 

 goto label_555556ac74ce ; 

 r9_6 = adl_process_counterparty_position ( clearinghouse_1 , 

 asset_idx_1 , & entry_addr_raw , & fill_delta , 

 & insolvent_user_addr , r9_5 ); 

```

```

 perform_auto_deleveraging) goto label_555556ac74ce;r9_6 = adl_process_counterparty_position(clearinghouse_1, asset_idx_1, &entry_addr_raw, &fill_delta, &insolvent_user_addr, r9_5);"> 

 So read the final 
```
 result . clear () 
```
 as a compact model of a no-execute mode, not as the literal place where the binary enforces the flag.

 Most importantly, for it to act it must actually be needed. What does that mean according to the 
```
 Clearinghouse 
```
?

## Threshold condition 

 The natural connection between liquidations and ADL is shortfall , which measures how much a position, or the entire system (!), is underwater.

 If we could liquidate every position in time against willing buyers of the debt, there would be no systemic shortfall. ADL is triggered whenever thatâs not the case.

### Who is underwater? 

 In order to determine that shortfall (or sum of bad debt) 1 , we process a useful tree of losing positions, built at the end of each block and passed to the 
```
 clearinghouse_adl_orchestrator () 
```
, starting from all user positions, which are stored in 
```
 clearinghouse . user_states 
```
, as we can also see from the serialization.

 exchange_end_block reaches adl_init_user_position_iterators directly, through build_adl_candidate_set, and through clearinghouse_adl_orchestrator. Call paths from exchange_end_block down to the position iterators exchange_end_block reaches adl_init_user_position_iterators directly, through build_adl_candidate_set, and through clearinghouse_adl_orchestrator. 

```
 exchange_end_block () 
```

```
 build_adl_candidate_set () 
```

```
 clearinghouse_adl_orchestrator () 
```

```
 adl_init_user_position_iterators () 
```

 - 
 The 
```
 adl_init_user_position_iterators () 
```
 essentially turns that into an 
```
 Iter 
```
, then, inside of 
```
 build_adl_candidate_set () 
```
 each entry is accounted either as a cross or isolated position, depending on the value of the 
```
 AdlIterEntry 
```
 field.

```
 struct AdlIterContext 
```
 
```

```
 struct AdlIterContext { 

 uint8_t * direction_ptr ; 

 struct OracleState * oracle_ptr ; 

 }; 

```

```

 Note that in storage, 
```
 Isolated 
```
 positions have their own independent 
```
 Entry 
```
 in the position iterators, and 
```
 Cross 
```
 positions have a single common 
```
 Entry 
```
, which will be spread across several perps. We will see many more branches to handle the two kinds of positions.

```
 build_adl_candidate_set () 
```
 
```

```
 152

 while ( true ) 

 153

 { 

 154

 int64_t shortfall_tag = entry_cursor -> margin_type ; 

 155

 if ( shortfall_tag != 2 ) 

 156

 { 

 157

 int64_t asset_idx = entry_cursor -> asset_idx ; 

 158

 } 

 159

 } 

```

```

 margin_type; if (shortfall_tag != 2) { int64_t asset_idx = entry_cursor->asset_idx; }}"> 

 Ultimately, we get an iterator of underwater users. Phase 1âs classify loop keeps only the entries whose account value is non-positive, which are the ones that could not be liquidated by the end of the block according to the earlier threshold. A positive value panics, since a solvent account should never reach ADL.

 After iterating over users, if the total losses are less than a predefined constant (hardcoded to $5M in the testnet state), we spare cross-margin positions and log 
```
Not performing auto-deleveraging because shortfall={} is acceptable.
```

 Note that this insurance fund is not applied to every asset. While this isnât documented anywhere, markets referred to as 
```
 only_isolated 
```
 (or 
```
 strict_isolated 
```
 in 
```
MessagePack
```
 dumps) are added to a separate queue, 
```
 deferred_queue 
```
, which triggers ADL regardless of the systemâs 
```
 total_shortfall 
```
. This is the 
```
 strict_isolated 
```
 branch in Phase 1 that we stepped through earlier.

 Very interestingly, some of the assets that have this flag, at least on testnet, include HYPE (and other relevant tokens like ZRO, as well as JELLYJELLY from the March 2025 incident ). Historical metadata for Hyperliquid is very hard to come by, so take this with a pinch of salt when thinking about mainnet. 2 

### How do we get rid of debt? 

 Now we know whenever we have shortfall. What is to be done in that case? This is where different risk engines make different design choices. Hyperliquid chooses to apply a queue-based ADL system, meaning they forcefully close some winning positions in order to clear the debt of the losing traders.

 Thus, if the debt is insurmountable, the 
```
 deferred_queue 
```
 is overwritten by all the users marked by 
```
 build_adl_candidate_set () 
```
. Otherwise we keep it, and only holders of underwater 
```
 strict_isolated 
```
 positions from the earlier loop are considered for ADL. That fork is Phase 2âs gate:

```
 clearinghouse_adl_orchestrator () 
```
 
```

```
 120

 let remaining_shortfall = ch . adl_shortfall_remaining . value ; 

 121

 let adl_was_triggered = total_shortfall_value >= remaining_shortfall ; 

 122

 if adl_was_triggered { 

 123

 deferred_cross_queue . clear (); 

 124

 let mut pointer_1 = candidates . iter (); 

 125

 while let Some (( counterparty_addr , asset_idx )) = pointer_1 . next () { 

 126

 deferred_cross_queue . push ((* counterparty_addr , * asset_idx )); 

 127

 } 

 128

 } 

```

```

 = remaining_shortfall;if adl_was_triggered { deferred_cross_queue.clear(); let mut pointer_1 = candidates.iter(); while let Some((counterparty_addr, asset_idx)) = pointer_1.next() { deferred_cross_queue.push((*counterparty_addr, *asset_idx)); }}"> 

 For each underwater position, Phase 3 does a B-tree lookup on 
```
 clearinghouse . user_states [ position . user ] 
```
 through the recovered 
```
 lookup_user_state () 
```
 helper and pushes the user onto a 
```
 Vec 
```
. You would be amazed at how long the compilation of such a simple statement is. This is the push alone, growth check included:

```
 clearinghouse_adl_orchestrator () 
```
 
```

```
 if ( cpty_vec_count == cpty_vec_cap ) 

 OPTION_UNIT_QTY_NONE_2 = vec_grow_0x28 (& cpty_vec_cap ); 

 int64_t rcx_11 = cpty_vec_count * 5 ; 

 *( cpty_vec_ptr + ( rcx_11 << 3 ) + 0x10 ) = scratch_opt.set.height ; 

 OPTION_UNIT_QTY_NONE_2 = scratch_opt.tag ; 

 *(& OPTION_UNIT_QTY_NONE_2 + 8 ) = scratch_opt.set.root_ptr ; 

 *( cpty_vec_ptr + ( rcx_11 << 3 )) = OPTION_UNIT_QTY_NONE_2 ; 

 *( cpty_vec_ptr + ( rcx_11 << 3 ) + 0x18 ) = deferred_entry_tag ; 

 *( cpty_vec_ptr + ( rcx_11 << 3 ) + 0x20 ) = entry_addr_raw_1 ; 

 cpty_vec_count += 1 ; 

```

```

 The logic for cross margin positions is more complicated, because weâre essentially asking the question of how to split a bankrupt userâs total shortfall across their individual positions, so that we can absorb the right proportion of each position. The natural split is to weight each position by its share of total cross notional:

 position_weight = position_notional total_cross_notional position_adl_amount = user_shortfall â position_weight \begin{aligned}
\text{position\_weight} &= \frac{\text{position\_notional}}{\text{total\_cross\_notional}} \\
\text{position\_adl\_amount} &= \text{user\_shortfall} \cdot \text{position\_weight}
\end{aligned} position_weight position_adl_amount â = total_cross_notional position_notional â = user_shortfall â position_weight â 
 In the four-phase sketch above, that proportional split is represented by the 
```
 build_counterparty_fills () 
```
 stub:

```
 clearinghouse_adl_orchestrator () 
```
 
```

```
 83

 fn build_counterparty_fills ( _ch : & Clearinghouse , _ctx : & mut AdlFillTracker , _oracle : & mut OracleData , _addr : &[ u8 ; 20 ], _asset_idx : u64 ) -> Vec < u8 > { 

 84

 Vec :: new () 

 85

 } 

```

```

 Vec { Vec::new()}"> 

 The real version spans all 
```
 ( asset_idx , direction ) 
```
 held in the cross margin position, weighting each by the formula above.

 For isolated positions the computation is trivial, and we directly write the single position, with its shortfall, to the 
```
 adl_output 
```
 B-tree, which is the output of this transformation for both isolated and cross margin positions, containing both 
```
 position_id 
```
 and 
```
 position_shortfall 
```
.

 Afterwards we can finally loop over the B-tree containing 
```
 ( position_id , cut ) 
```
, which essentially tells us exactly how much of each position needs to be closed, to be later deleveraged from a winning position.

 The final phase of 
```
 clearinghouse_adl_orchestrator () 
```
 iterates it, and for each key it builds a counterparty array, initially including all users holding positions, sorting them based on a per-asset ADL ranking score. 3 

 How are positions chosen (sorted) to be deleveraged?

## Who do we deleverage? 

 This question is essential to the solvency and fairness of a perp platform. It is clear why solvency is a priority here.

 But what do we mean by fairness? Colloquially, we can say that the relative wealth of accounts should not be affected by deleveraging.

 More formally, fairness can be given multiple related definitions. See this paper for one treatment. We want to prove that the algorithm used in HL is not axiomatically fair in its implementation, as defined in prop. 6.1 of the paper.

 So, is Hyperliquid fair? Is it always solvent?

## ADL score computation 

 The score function at 
```
 compute_adl_ranking_score () 
```
 is core to answering this question. Itâs defined, most likely as an 
```
 Ord 
```
 implementation on some 20-byte address representation. A 
```
 Vec 
```
 of those holds the possible counterparties to fill against, and the trait is used by the sort routines that order them by ranking score for each underwater position.

 Those sort routines are generated by the compiler . Since Rust binaries include a lot of metadata by default in 
```
.comment
```
, we may even manually take advantage of this to recover the exact source of library functions .

 Letâs see how this ties back into the 
```
 clearinghouse_adl_orchestrator () 
```
:

 clearinghouse_adl_orchestrator reaches compute_adl_ranking_score through the compiler-generated driftsort and quicksort routines. Call paths from the orchestrator to the ADL ranking score clearinghouse_adl_orchestrator reaches compute_adl_ranking_score through the compiler-generated driftsort and quicksort routines. 

```
 clearinghouse_adl_orchestrator () 
```

```
 driftsort_smallsort_insertion_by_adl_ranking () 
```

```
 adl_quicksort_by_ranking () 
```

```
 sub_555556bd15e0 () 
```

```
 driftsort_quicksort_by_adl_ranking () 
```

```
 compute_adl_ranking_score () 
```

 - 
 The sort itself is generated by the compiler, so there is no single hand-written call site to point at. The orchestrator hands its counterparties to those routines, which call back into 
```
 compute_adl_ranking_score () 
```
 for every comparison.

### Ratio 1: effective leverage 

 Definition (Effective leverage) effectiveÂ leverage = â£ notional â£ accountÂ value \text{effective leverage} = \frac{|\text{notional}|}{\text{account value}} effectiveÂ leverage = accountÂ value â£ notional â£ â In the recovered score function, the first ratio is the positionâs absolute notional over its account value, which is the risk multiplier the user took on.

```
 compute_adl_ranking_score () 
```
 
```

```
 154

 let abs_notional = ( signed_notional_product as f64 ). abs (); 

 155

 let account_value = result_2 . account_value_unit . qty as f64 ; 

 156

 let ratio1_margin_ratio = ( abs_notional / account_value ). max ( 1 e- 8 ); 

```

```

 Note (Operand check) The lower-level decompiler comment around 
```
 label_555556abb73f 
```
 labels this ratio as 
```
 account_value / abs_notional 
```
, but the raw instruction operands settle it the other way. The numerator uses the unsigned 
```
u64 â f64
```
 SIMD conversion pattern, which matches 
```
 abs_notional 
```
. The denominator uses signed 
```
cvtsi2sd
```
, which matches 
```
 account_value 
```
. The final 
```
 divsd 
```
 computes numerator over denominator.

### Ratio 2: profit ratio 

 Definition (Profit ratio) profitÂ ratio = max â¡ ( pnl , â 0 ) entryÂ notional \text{profit ratio} = \frac{\max(\text{pnl},\, 0)}{\text{entry notional}} profitÂ ratio = entryÂ notional max ( pnl , 0 ) â The second ratio divides the positionâs PnL, clamped to non-negative, by its entry notional, telling us how well the userâs bet went.[^4]

```
 compute_adl_ranking_score () 
```
 
```

```
 158

 let result_4 = ( signed_notional_product + entry_notional_1 ). max ( 0 ) as f64 ; 

 159

 let result = ratio1_margin_ratio * ( result_4 / ( entry_notional_4 as f64 )). max ( 1 e- 8 ); 

```

```

 There is clamping to avoid rounding issues. Both ratios are clamped to a minimum of 
```
 1 e- 8 
```
, in order not to cancel each other out. The final ADL ranking score is 
```
 effective_leverage * profit_ratio 
```
, consistent with both the recovered Rust and the raw operand check.

 Intuition We look for risky and profitable positions!

## Partial and total ADL 

 Finally, note that deleveraging can also be partial, but even then it goes by the order defined by this score.

 Here, we fork based on whether ADL is total or not, closing the position in the former case. In the binary view, that decision compares the counterpartyâs position size against the shortfall left to fill:

```
 clearinghouse_adl_orchestrator () 
```
 
```

```
 if ( cpty_pos_size <= fill_remaining_check_2 ) 

 { 

 // Full fill pops the consumed counterparty and takes the entire position. 

 cpty_ranking_count -= 1 ; 

 // ... 

 fill_delta . value = cpty_pos_abs_szi ; 

 } 

```

```

 So essentially, the whole latter part of 
```
 clearinghouse_adl_orchestrator () 
```
 boils down to Phase 4, which runs the fills per asset and direction:

```
 clearinghouse_adl_orchestrator () 
```
 
```

```
 143

 let mut pointer_3 = result . iter_mut (); 

 144

 while let Some ((&( asset_idx , expected_kind ), counterparty_info )) = pointer_3 . next () { 

 145

 let length = counterparty_info . len (); 

 146

 let mut i : usize = 0 ; 

 147

 while i < length { 

 148

 let cpty_addr_bytes = counterparty_info [ i ]; 

 149

 let fill_delta = process_counterparty_fill ( ch , fill_ctx , oracle , asset_idx , expected_kind , cpty_addr_bytes ); 

 150

 let _ = fill_delta ; 

 151

 i = i . wrapping_add ( 1 ); 

 152

 } 

 153

 } 

```

```

 The execution-gate caveat above applies to this call. 4 The binary only performs the forced-close operation when 
```
 perform_auto_deleveraging 
```
 is set.

 Note that 
```
 fill . pos_szi 
```
 is the full position size of the insolvent user, not just the position shortfall. This is key to understanding the financial implications of ADL.

## Branches 

 There is still much to be explored here. We could try to take a leap forward and conjecture some financial conclusions from what weâve learned so far, or we could take a step back and do some introspection on the tools that made this all possible.

 Given the polar opposite direction of those two ends, the author has decided to let the reader choose their own adventure.

## Financial conclusions 

## Fairness, revenue, solvency trilemma 

 Aligning with the trilemma proposed in Â§2.1, prop. 2.5 of the paper mentioned before , letâs try to quantify a concrete estimate for each axis of the trilemma:

- Solvency measures whether the platform can pay every trader out.

- Fairness uses the axiomatic fairness definition per prop. 3.4.

- Revenue measures the fraction of total winner PNL that survives after deleveraging.

 Letâs borrow these definitions from the paper.

 Notation P n : = markÂ price I : = insuranceÂ fund c i : = collateral = notional leverage Ï i = s i â ( P n â p i ) e i = c i + Ï i w i = Ï i + x i : = dollarsÂ seizedÂ fromÂ winnerÂ i h i = x i w i H T = â i x i D T = â i max â¡ ( â e i , â 0 ) U T = â i w i R t = max â¡ ( D T â I â H T , â 0 ) \begin{aligned}
P_n &:= \text{mark price} \\
I &:= \text{insurance fund} \\
c_i &:= \text{collateral} = \frac{\text{notional}}{\text{leverage}} \\
\pi_i &= s_i \cdot (P_n - p_i) \\
e_i &= c_i + \pi_i \\
w_i &= \pi_i^+ \\
x_i &:= \text{dollars seized from winner } i \\
h_i &= \frac{x_i}{w_i} \\
H_T &= \sum_i x_i \\
D_T &= \sum_i \max(-e_i,\, 0) \\
U_T &= \sum_i w_i \\
R_t &= \max(D_T - I - H_T,\, 0)
\end{aligned} P n â I c i â Ï i â e i â w i â x i â h i â H T â D T â U T â R t â â := markÂ price := insuranceÂ fund := collateral = leverage notional â = s i â â ( P n â â p i â ) = c i â + Ï i â = Ï i + â := dollarsÂ seizedÂ fromÂ winnerÂ i = w i â x i â â = i â â x i â = i â â max ( â e i â , 0 ) = i â â w i â = max ( D T â â I â H T â , 0 ) â Here, P n P_n P n â is the mark price from different sources, I I I is the insurance fund, roughly the 5M on testnet HL, Ï i \pi_i Ï i â is PNL for longs and negated for shorts, and w i w_i w i â is the positive part of PNL.

 And letâs make the trilemma definitions concrete.

- Solvency is 1 â R t D T 1 - \frac{R_t}{D_T} 1 â D T â R t â â . It measures how much of the total bad debt was actually covered. S = 1 S=1 S = 1 means fully solvent ( R t = 0 R_t=0 R t â = 0 ), while S = 0 S=0 S = 0 means nothing was recovered.

- Fairness is 1 â Gini ( h i ) 1 - \text{Gini}(h_i) 1 â Gini ( h i â ) , where h i = x i / w i h_i = x_i / w_i h i â = x i â / w i â for each winner with w i > 0 w_i > 0 w i â > 0 . It measures how uniformly the haircut burden is distributed across profitable traders. F = 1 F=1 F = 1 means everyone loses the same fraction of their PNL. F â 0 F \approx 0 F â 0 means a few get wiped while most are untouched.

- Revenue is U T Ï / U T U_T^\pi / U_T U T Ï â / U T â . Here U T Ï U_T^\pi U T Ï â is the haircut capacity, or total positive PNL, after going through a policy Ï \pi Ï .

 We can now simulate these values for both Hyperliquid and Percolator, a new pro-rata based perp engine developed by Anatoly Yakovenko ( github.com/aeyakovenko/percolator ).

 We fix an a priori price path to simulate two cases. The first is a crash followed by a recovery, and the second is a crash followed by an equally severe second crash. This is the most common reason for deleveraging, but the opposite move could also trigger the same machinery.

 One prediction that we can make is that Percolator is perfectly fair according to this scoring because the h i h_i h i â are the same for everyone. The Gini coefficient must therefore be 0.

 We are ignoring the a posteriori price impact that deleveraging causes (read about the Oct 10 crash analysis in that paper). Cross-margin leverage is also interesting because it introduces more correlation between cross-traded assets, while with Percolator we have one risk engine per asset (slab).

 Hyperliquid also has an interesting caveat we showed earlier, as it operates with a conditional insurance fund. We will simulate a single asset for now, but this influences the equation when we have multiple assets being traded in either isolated or cross-margin mode.

## Simulations 

 Letâs consider the following price scenarios:

 Running this simulation of both systems with a Python reimplementation yields these results:

### Percolator is more âoptimisticâ 

 The key difference is what happens to positions. ADL permanently closes them. If the market keeps moving in your favor, tough luck, youâre already out and have to re-enter at the new price. Percolator only reduces what you can withdraw , but the position stays open. If conditions improve, 
```
 Residual 
```
 goes up, 
```
h
```
 climbs back toward 1, and you get your PNL back without doing anything.

 We can see this in a short squeeze scenario (60% short market, price +10%). HLâs queue closes 8 of the 27 winning longs â those traders get zero if the rally continues. Under Percolator, all 27 keep their full positions (only the withdrawable profit is reduced by the uniform haircut) and all participate in the continued move. Note that HLâs surviving positions are at full size, so they individually capture more per position, though the tradeoff is that fewer traders get to participate.

## Percolator is indifferent to leverage 

 We can prove that this is quite the opposite for Hyperliquid, as weâve traced the implementation of the ADL algorithm, which disproportionately targets higher leverage.

## Fairness 

 A point made in the same paper is that Hyperliquid is âantifairâ. The node implementation chooses positions in descending score order, closes them, and leaves everything else untouched.

 The paper already states in prop. 8.1 that queue-based algos like HL reach solvency faster. We can see that by looking at how ADL is triggered. In 
```
 clearinghouse_adl_orchestrator () 
```
 we start by fully closing the worst position against the best-performing trader.

## Strengths and limitations of agents for reverse engineering 

 In general, the lionâs share of the work is done by the underlying model, save for very straightforward tasks. Pushing the model too hard toward a fixed set of possible conclusions usually makes it worse at search problems.

## Hooks 

 Tools are excellent at checking the agentâs work via hooks . The agent proposes a solution to an uncertain problem, such as type recovery, and the hook checks whether that type has compatible offsets and nested pointers compared to what is really used at the assembly level. We applied a similar, simpler check to data flow in the reconstructed Rust snippets.

 At the same time, thereâs a very thin line between readable output with no validation, and output that is unreadable but technically passes according to the hook. In general, hooks trade time and readability for concrete properties that can be checked at each stage, for example whether the Rust sample compiles and uses variables that map 1 to the disassembly.

## Scale 

 The second lesson to be learned is that agents really shine at scale. Newer models can hold more context than the best reverse engineers out there, so using them for bulk looped tasks like renaming many functions is optimal.

 That being said, agents are also far more overconfident than the best reverse engineers. In setups where the agent has tools that âwriteâ to the decompiler view, wrong guesses compounded across recovery stages. The tool layer helped by forcing failed guesses back into analysis, which gave the agent more data before it tried the harder questions again.

## Whatâs next? 

 This is by no means a strict scientific verdict, but rather some field notes. The public source code for the agents and their tools can be found over at this GitHub repo .

 The analyzed binary is available as hl-node (53 MB).

## Closing words 

 As much as it would be exciting to say that everything can be cracked open and studied in the age of LLMs, there are still some gaps to bridge.

 Flagship models got us 60% of the way there, but a lot of manual work is still required. We still need to document patterns in the Rust compiler, distill that knowledge onto agents and tools, and understand the âwhysâ behind a program, beyond the technical question of the âwhatâ.

 Still, there is no doubt that LLMs have greatly accelerated progress in the field, and the dream of throwing a well-armed swarm of agents at an ugly blob of machine code to extract meaningful and, most importantly, correct representations and source code is nearing.

 We hope to be part of that future, where even complex and obfuscated systems will be verifiable at a glance.

## Footnotes 

- 
 
```
 compute_user_margin_and_shortfall () 
```
 is a ubiquitous function for accounting. In its main branch, we loop over a B-tree (note the repeating offsets 
```
0x748
```
 in the abstract expressions of 
```
 btree_cursor 
```
) of per-user positions, branching out based on cross/isolated positions (in order to know what to consider for notional). â© 

- 
 Some of the historical data from Hyperliquid can be retrieved via the 
```
s3://hl-mainnet-node-data/explorer_blocks
```
 S3 bucket. â© 

- 
 Some loop iterations within the ADL code look very inefficient. For example, we seem to sort and come up with sorted counterparties for each position to be absorbed. â© 

- 
 ADL crashes the node upon failure. Specifically, if we donât manage to complete all of the fills against anybody, an assertion in the loop fails. â©

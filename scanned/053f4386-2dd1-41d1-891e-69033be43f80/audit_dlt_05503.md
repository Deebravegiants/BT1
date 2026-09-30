# [?] Fix overflow (#84)

## Summary
Severity: Unknown
Chain: Solana
Component: raydium-io/raydium-clmm
Published: 2024-08-13
Source: https://github.com/raydium-io/raydium-clmm/commit/946dc44b779e78665552944a844d8193990b6a56
Type: security-commit

## Details
Fix overflow (#84)

* Fix: fix for overflow while calculate amount

* Fix: fix for stack overflow about U512 overflowing_pow

* optimizate limit price

* catch overflow when calculate amount from liquidity

---------

Co-authored-by: 0x777A <eddy@raydium.io>

## Patch
### Cargo.lock
```diff
@@ -5838,8 +5838,7 @@ checksum = "42ff0bf0c66b8238c6f3b578df37d0b7848e55df8577b3f74f92a69acceeb825"
 [[package]]
 name = "uint"
 version = "0.9.5"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "76f64bba2c53b04fcab63c01a7d7427eadc821e3bc48c34dc9ba29c501164b52"
+source = "git+https://github.com/raydium-io/parity-common#43a0303b9c2a23a00508816bd6d5a2e9381f143c"
 dependencies = [
  "byteorder",
  "crunchy",
```

### client/src/instructions/utils.rs
```diff
@@ -471,7 +471,9 @@ fn swap_compute(
             fee,
             is_base_input,
             zero_for_one,
-        );
+            1,
+        )
+        .unwrap();
         state.sqrt_price_x64 = swap_step.sqrt_price_next_x64;
         step.amount_in = swap_step.amount_in;
         step.amount_out = swap_step.amount_out;
```

### programs/amm/Cargo.toml
```diff
@@ -27,7 +27,7 @@ anchor-lang = { version = "0.29.0", features = ["init-if-needed"] }
 anchor-spl = {version = "0.29.0", features = ["metadata"]}
 solana-program = "<1.17.0"
 spl-memo = "4.0.0"
-uint = "0.9.1"
+uint = { git = "https://github.com/raydium-io/parity-common", package = "uint" }
 mpl-token-metadata = { version = "^1.11.0", features = ["no-entrypoint"] }
 bytemuck = { version = "1.4.0", features = ["derive", "min_const_generics"] }
 arrayref = { version = "0.3.6" }
```

### programs/amm/src/error.rs
```diff
@@ -61,7 +61,7 @@ pub enum ErrorCode {
     #[msg("Too much input paid")]
     TooMuchInputPaid,
     #[msg("Swap special amount can not be zero")]
-    InvaildSwapAmountSpecified,
+    ZeroAmountSpecified,
     #[msg("Input pool vault is invalid")]
     InvalidInputPoolVault,
     #[msg("Swap input or output amount is too small")]
@@ -101,4 +101,8 @@ pub enum ErrorCode {
     MissingTickArrayBitmapExtensionAccount,
     #[msg("Insufficient liquidity for this direction")]
     InsufficientLiquidityForDirection,
+    #[msg("Max token overflow")]
+    MaxTokenOverflow,
+    #[msg("calculate overflow")]
+    CalculateOverflow,
 }
```

### programs/amm/src/instructions/admin/update_pool_status.rs
```diff
@@ -12,10 +12,7 @@ pub struct UpdatePoolStatus<'info> {
     pub pool_state: AccountLoader<'info, PoolState>,
 }
 
-pub fn update_pool_status(
-    ctx: Context<UpdatePoolStatus>,
-    status: u8,
-) -> Result<()> {
+pub fn update_pool_status(ctx: Context<UpdatePoolStatus>, status: u8) -> Result<()> {
     require_gte!(255, status);
     let mut pool_state = ctx.accounts.pool_state.load_mut()?;
     pool_state.set_status(status);
```

### programs/amm/src/instructions/close_position.rs
```diff
@@ -3,7 +3,7 @@ use crate::states::*;
 use crate::util::{burn, close_spl_account};
 use anchor_lang::prelude::*;
 use anchor_spl::token::Token;
-use anchor_spl::token_interface::{Mint,TokenAccount};
+use anchor_spl::token_interface::{Mint, TokenAccount};
 
 #[derive(Accounts)]
 pub struct ClosePosition<'info> {
@@ -78,16 +78,15 @@ pub fn close_position<'a, 'b, 'c, 'info>(
         }
     }
 
-        burn(
-            &ctx.accounts.nft_owner,
-            &ctx.accounts.position_nft_mint,
-            &ctx.accounts.position_nft_account,
-            &ctx.accounts.token_program,
-            // &ctx.accounts.token_program_2022,
-            &[],
-            1,
-        )?;
-    
+    burn(
+        &ctx.accounts.nft_owner,
+        &ctx.accounts.position_nft_mint,
+        &ctx.accounts.position_nft_account,
+        &ctx.accounts.token_program,
+        // &ctx.accounts.token_program_2022,
+        &[],
+        1,
+    )?;
 
     close_spl_account(
         &ctx.accounts.nft_owner,
```

### programs/amm/src/instructions/swap.rs
```diff
@@ -150,7 +150,7 @@ pub fn swap_internal<'b, 'info>(
     is_base_input: bool,
     block_timestamp: u32,
 ) -> Result<(u64, u64)> {
-    require!(amount_specified != 0, ErrorCode::InvaildSwapAmountSpecified);
+    require!(amount_specified != 0, ErrorCode::ZeroAmountSpecified);
     if !pool_state.get_status_by_bit(PoolStatusBitIndex::Swap) {
         return err!(ErrorCode::NotApproved);
     }
@@ -214,6 +214,10 @@ pub fn swap_internal<'b, 'info>(
     // continue swapping as long as we haven't used the entire input/output and haven't
     // reached the price limit
     while state.amount_specified_remaining != 0 && state.sqrt_price_x64 != sqrt_price_limit_x64 {
+        // println!(
+        //     "state.amount_specified_remaining:{}",
+        //     state.amount_specified_remaining
+        // );
         #[cfg(feature = "enable-log")]
         msg!(
             "while begin, is_base_input:{},fee_growth_global_x32:{}, state_sqrt_price_x64:{}, state_tick:{},state_liquidity:{},state.protocol_fee:{}, protocol_fee_rate:{}",
@@ -318,7 +322,8 @@ pub fn swap_internal<'b, 'info>(
             amm_config.trade_fee_rate,
             is_base_input,
             zero_for_one,
-        );
+            block_timestamp,
+        )?;
         #[cfg(feature = "enable-log")]
         msg!("{:#?}", swap_step);
         if zero_for_one {
@@ -345,10 +350,15 @@ pub fn swap_internal<'b, 'info>(
                 .amount_specified_remaining
                 .checked_sub(step.amount_out)
                 .unwrap();
+
+            let step_amount_calculate = step
+                .amount_in
+                .checked_add(step.fee_amount)
+                .ok_or(ErrorCode::CalculateOverflow)?;
             state.amount_calculated = state
                 .amount_calculated
-                .checked_add(step.amount_in + step.fee_amount)
-                .unwrap();
+                .checked_add(step_amount_calculate)
+                .ok_or(ErrorCode::CalculateOverflow)?;
         }
 
         let step_fee_amount = step.fee_amount;
@@ -786,12 +796,18 @@ pub fn swap<'a, 'b, 'c: 'info, 'info>(
 
 #[cfg(test)]
 mod swap_test {
+    use liquidity_math::get_delta_amounts_signed;
+    use tick_array_bitmap_extension_test::{
+        build_tick_array_bitmap_extension_info, BuildExtensionAccountInfo,
+    };
+
     use super::*;
     use crate::states::pool_test::build_pool;
     use crate::states::tick_array_test::{
         build_tick, build_tick_array_with_tick_states, TickArrayInfo,
     };
     use std::cell::RefCell;
+    use std::collections::HashMap;
     use std::vec;
 
     pub fn get_tick_array_states_mut(
@@ -844,6 +860,226 @@ mod swap_test {
         (amm_config, pool_state, tick_array_states, observation_state)
     }
 
+    pub struct OpenPositionParam {
+        pub amount_0: u64,
+        pub amount_1: u64,
+        // pub liquidity: u128,
+        pub tick_lower: i32,
+        pub tick_upper: i32,
+    }
+
+    fn setup_swap_test<'info>(
+        start_tick: i32,
+        tick_spacing: u16,
+        position_params: Vec<OpenPositionParam>,
+        zero_for_one: bool,
+    ) -> (
+        AmmConfig,
+        RefCell<PoolState>,
+        VecDeque<RefCell<TickArrayState>>,
+        RefCell<ObservationState>,
+        TickArrayBitmapExtension,
+        u64,
+        u64,
+    ) {
+        let amm_config = AmmConfig {
+            trade_fee_rate: 1000,
+            tick_spacing,
+            ..Default::default()
+        };
+
+        let pool_state_refcel = build_pool(
+            start_tick,
+            tick_spacing,
+            tick_math::get_sqrt_price_at_tick(start_tick).unwrap(),
+            0,
+        );
+
+        let observation_state = RefCell::new(ObservationState::default());
+
+        let param = &mut BuildExtensionAccountInfo::default();
+        param.key = Pubkey::find_program_address(
+            &[
+                POOL_TICK_ARRAY_BITMAP_SEED.as_bytes(),
+                pool_state_refcel.borrow().key().as_ref(),
+            ],
+            &crate::id(),
+        )
+        .0;
+        let bitmap_extension = build_tick_array_bitmap_extension_info(param);
+        let mut tick_array_states: VecDeque<RefCell<TickArrayState>> = VecDeque::new();
+        let mut sum_amount_0: u64 = 0;
+        let mut sum_amount_1: u64 = 0;
+        {
+            let mut pool_state = pool_state_refcel.borrow_mut();
+            observation_state.borrow_mut().pool_id = pool_state.key();
+
+            let mut tick_array_map = HashMap::new();
+
+            for position_param in position_params {
+                let liquidity = liquidity_math::get_liquidity_from_amounts(
+                    pool_state.sqrt_price_x64,
+                    tick_math::get_sqrt_price_at_tick(position_param.tick_lower).unwrap(),
+                    tick_math::get_sqrt_price_at_tick(position_param.tick_upper).unwrap(),
+                    position_param.amount_0,
+                    position_param.amount_1,
+                );
+
+                let (amount_0, amount_1) = get_delta_amounts_signed(
+                    start_tick,
+                    tick_math::get_sqrt_price_at_tick(start_tick).unwrap(),
+                    position_param.tick_lower,
+                    position_param.tick_upper,
+                    liquidity as i128,
+                )
+                .unwrap();
+                sum_amount_0 += amount_0;
+                sum_amount_1 += amount_1;
+                let tick_array_lower_start_index =
+                    TickArrayState::get_array_start_index(position_param.tick_lower, tick_spacing);
+
+                if !tick_array_map.contains_key(&tick_array_lower_start_index) {
+                    let mut tick_array_refcel = build_tick_array_with_tick_states(
+                        pool_state.key(),
+                        tick_array_lower_start_index,
+                        tick_spacing,
+                        vec![],
+                    );
+                    let tick_array_lower = tick_array_refcel.get_mut();
+
+                    let tick_lower = tick_array_lower
+                        .get_tick_state_mut(position_param.tick_lower, tick_spacing)
+                        .unwrap();
+                    tick_lower.tick = position_param.tick_lower;
+                    tick_lower
+                        .update(
+                            pool_state.tick_current,
+                            i128::try_from(liquidity).unwrap(),
+                            0,
+                            0,
+                            false,
+                            &[RewardInfo::default(); 3],
+                        )
+                        .unwrap();
+
+                    tick_array_map.insert(tick_array_lower_start_index, tick_array_refcel);
+                } else {
+                    let tick_array_lower = tick_array_map
+                        .get_mut(&tick_array_lower_start_index)
+                        .unwrap();
+                    let mut tick_array_lower_borrow_mut = tick_array_lower.borrow_mut();
+                    let tick_lower = tick_array_lower_borrow_mut
+                        .get_tick_state_mut(position_param.tick_lower, tick_spacing)
+                        .unwrap();
+
+                    tick_lower
+                        .update(
+                            pool_state.tick_current,
+                            i128::try_from(liquidity).unwrap(),
+                            0,
+                            0,
+                            false,
+                            &[RewardInfo::default(); 3],
+                        )
+                        .unwrap();
+                }
+                let tick_array_upper_start_index =
+                    TickArrayState::get_array_start_index(position_param.tick_upper, tick_spacing);
+                if !tick_array_map.contains_key(&tick_array_upper_start_index) {
+                    let mut tick_array_refcel = build_tick_array_with_tick_states(
+                        pool_state.key(),
+                        tick_array_upper_start_index,
+                        tick_spacing,
+                        vec![],
+                    );
+                    let tick_array_upper = tick_array_refcel.get_mut();
+
+                    let tick_upper = tick_array_upper
+                        .get_tick_state_mut(position_param.tick_upper, tick_spacing)
+                        .unwrap();
+                    tick_upper.tick = position_param.tick_upper;
+
+                    tick_upper
+                        .update(
+                            pool_state.tick_current,
+                            i128::try_from(liquidity).unwrap(),
+                            0,
+                            0,
+                            true,
+                            &[RewardInfo::default(); 3],
+                        )
+                        .unwrap();
+
+                    tick_array_map.insert(tick_array_upper_start_index, tick_array_refcel);
+                } else {
+                    let tick_array_upper = tick_array_map
+                        .get_mut(&tick_array_upper_start_index)
+                        .unwrap();
+
+                    let mut tick_array_upperr_borrow_mut = tick_array_upper.borrow_mut();
+                    let tick_upper = tick_array_upperr_borrow_mut
+                        .get_tick_state_mut(position_param.tick_upper, tick_spacing)
+                        .unwrap();
+
+                    tick_upper
+                        .update(
+                            pool_state.tick_current,
+                            i128::try_from(liquidity).unwrap(),
+                            0,
+                            0,
+                            true,
+                            &[RewardInfo::default(); 3],
+                        )
+                        .unwrap();
+                }
+                if pool_state.tick_current >= position_param.tick_lower
+                    && pool_state.tick_current < position_param.tick_upper
+                {
+                    pool_state.liquidity = liquidity_math::add_delta(
+                        pool_state.liquidity,
+                        i128::try_from(liquidity).unwrap(),
+                    )
+                    .unwrap();
+                }
+            }
+            for (tickarray_start_index, tick_array_info) in tick_array_map {
+                tick_array_states.push_back(tick_array_info);
+                pool_state
+                    .flip_tick_array_bit(Some(&bitmap_extension), tickarray_start_index)
+                    .unwrap();
+            }
+
+            use std::convert::identity;
+            if zero_for_one {
+                tick_array_states.make_contiguous().sort_by(|a, b| {
+                    identity(b.borrow().start_tick_index)
+                        .cmp(&identity(a.borrow().start_tick_index))
+                });
+            } else {
+                tick_array_states.make_contiguous().sort_by(|a, b| {
+                    identity(a.borrow().start_tick_index)
+                        .cmp(&identity(b.borrow().start_tick_index))
+                });
+            }
+        }
+        let bitmap_extension_state =
+            *AccountLoader::<TickArrayBitmapExtension>::try_from(&bitmap_extension)
+                .unwrap()
+                .load()
+                .unwrap()
+                .deref();
+
+        (
+            amm_config,
+            pool_state_refcel,
+            tick_array_states,
+            observation_state,
+            bitmap_extension_state,
+            sum_amount_0,
+            sum_amount_1,
+        )
+    }
+
     #[cfg(test)]
     mod cross_tick_array_test {
         use super::*;
@@ -1645,4 +1881,393 @@ mod swap_test {
             );
         }
     }
+
+    #[cfg(test)]
+    mod sqrt_price_limit_optimization_test {
+        use super::*;
+        use proptest::prelude::*;
+        use std::{convert::identity, u64};
+
+        use proptest::prop_assume;
+        proptest! {
+                    #![proptest_config(ProptestConfig::with_cases(2048))]
+                    #[test]
+                    fn zero_for_one_base_input_test(
+                        tick_current in tick_math::MIN_TICK..tick_math::MAX_TICK,
+                        amount_0 in 1000000..u64::MAX,
+                        amount_1 in 1000000..u64::MAX,
+                        tick_lower in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 10", |x| x % 10 == 0),
+                        tick_upper in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 10", |x| x % 10 == 0),
+                    ){
+                        let tick_spacing = 10;
+                        let zero_for_one = true;
+                        let is_base_input = true;
+                        if tick_lower%tick_spacing ==0 && tick_upper%tick_spacing ==0 && tick_upper>tick_lower{
+
+
+                            let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state,  sum_amount_0, sum_amount_1) = setup_swap_test(
+                                tick_current,
+                                tick_spacing as u16,
+                                vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                zero_for_one
+                                );
+
+                            prop_assume!(sum_amount_1 > 1);
+                            let mut rng = rand::thread_rng();
+                            let amount_specified  = rng.gen_range(1..u64::MAX - sum_amount_0);
+
+                            let result = swap_internal(
+                                &amm_config,
+                                &mut pool_state.borrow_mut(),
+                                &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                &mut observation_state.borrow_mut(),
+                                &Some(bitmap_extension_state),
+                                amount_specified,
+                                tick_math::MIN_SQRT_PRICE_X64 + 1,
+                                zero_for_one,
+                                is_base_input,
+                                0,
+                            );
+
+
+
+                            if result.is_ok() {
+                                let ( amount_0_before, amount_1_before) = result.unwrap();
+
+                                let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state,  _sum_amount_0, _sum_amount_1) = setup_swap_test(
+                                    tick_current,
+                                    tick_spacing as u16,
+                                    vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                    zero_for_one
+                                );
+                                let result = swap_internal(
+                                    &amm_config,
+                                    &mut pool_state.borrow_mut(),
+                                    &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                    &mut observation_state.borrow_mut(),
+                                    &Some(bitmap_extension_state),
+                                    amount_specified,
+                                    tick_math::MIN_SQRT_PRICE_X64 + 1,
+                                    zero_for_one,
+                                    is_base_input,
+                                    oracle::block_timestamp_mock() as u32,
+                                );
+                                assert!(result.is_ok());
+
+                                // println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{},liquidity:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper, identity(pool_state.borrow().liquidity));
+
+                                    let ( amount_0_after, amount_1_after) = result.unwrap();
+                                    assert_eq!(amount_0_before, amount_0_after);
+                                    assert_eq!(amount_1_before, amount_1_after);
+
+                            }else{
+                                let err =  result.err().unwrap();
+                                if err == crate::error::ErrorCode::MaxTokenOverflow.into(){
+                                    println!("##### original swap is overflow ");
+                                    let result = swap_internal(
+                                        &amm_config,
+                                        &mut pool_state.borrow_mut(),
+                                        &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                        &mut observation_state.borrow_mut(),
+                                        &Some(bitmap_extension_state),
+                                        amount_specified,
+                                        tick_math::MIN_SQRT_PRICE_X64 + 1,
+                                        zero_for_one,
+                                        is_base_input,
+                                        oracle::block_timestamp_mock() as u32,
+                                    );
+                                    if result.is_err(){
+                                        println!("{:#?}", result);
+                                    }
+                                }else{
+                                    println!("{}", err);
+                                }
+                            }
+                        }
+                    }
+
+                    #[test]
+                    fn zero_for_one_base_output_test(
+                        tick_current in tick_math::MIN_TICK..tick_math::MAX_TICK,
+                        amount_0 in 1000000..u64::MAX,
+                        amount_1 in 1000000..u64::MAX,
+                        tick_lower in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 100", |x| x % 10 == 0),
+                        tick_upper in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 100", |x| x % 10 == 0),
+                    ){
+                        let tick_spacing = 10;
+                        let zero_for_one = true;
+                        let base_input= false;
+                        if tick_lower%tick_spacing ==0 && tick_upper%tick_spacing ==0 && tick_upper>tick_lower{
+
+
+                            let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state, _sum_amount_0, sum_amount_1) = setup_swap_test(
+                                tick_current,
+                                tick_spacing as u16,
+                                vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                zero_for_one
+                            );
+
+                            prop_assume!(sum_amount_1 > 1);
+                            let mut rng = rand::thread_rng();
+                            let amount_specified  = rng.gen_range(1..sum_amount_1);
+
+                            // println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper);
+
+
+                            let result = swap_internal(
+                                &amm_config,
+                                &mut pool_state.borrow_mut(),
+                                &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                &mut observation_state.borrow_mut(),
+                                &Some(bitmap_extension_state),
+                                amount_specified,
+                                tick_math::MIN_SQRT_PRICE_X64 + 1,
+                                zero_for_one,
+                                base_input,
+                                0,
+                            );
+
+
+                            if result.is_ok() {
+                                let ( amount_0_before, amount_1_before) = result.unwrap();
+
+                                let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state, _sum_amount_0, _sum_amount_1) = setup_swap_test(
+                                    tick_current,
+                                    tick_spacing as u16,
+                                    vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                    zero_for_one
+                                );
+                                let result = swap_internal(
+                                    &amm_config,
+                                    &mut pool_state.borrow_mut(),
+                                    &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                    &mut observation_state.borrow_mut(),
+                                    &Some(bitmap_extension_state),
+                                    amount_specified,
+                                    tick_math::MIN_SQRT_PRICE_X64 + 1,
+                                    zero_for_one,
+                                    base_input,
+                                    oracle::block_timestamp_mock() as u32,
+                                );
+                                assert!(result.is_ok());
+
+                                println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{},liquidity:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper, identity(pool_state.borrow().liquidity));
+
+                                    let ( amount_0_after, amount_1_after) = result.unwrap();
+                                    assert_eq!(amount_0_before, amount_0_after);
+                                    assert_eq!(amount_1_before, amount_1_after);
+
+                            }else{
+                                let err =  result.err().unwrap();
+                                if err == crate::error::ErrorCode::MaxTokenOverflow.into(){
+                                    println!("##### original swap is overflow");
+                                    let result = swap_internal(
+                                        &amm_config,
+                                        &mut pool_state.borrow_mut(),
+                                        &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                        &mut observation_state.borrow_mut(),
+                                        &Some(bitmap_extension_state),
+                                        amount_specified,
+                                        tick_math::MIN_SQRT_PRICE_X64 + 1,
+                                        zero_for_one,
+                                        base_input,
+                                        oracle::block_timestamp_mock() as u32,
+                                    );
+                                    if result.is_err(){
+                                        println!("{:#?}", result);
+                                    }
+                                }else{
+                                    println!("{}", err);
+                                }
+                            }
+                        }
+                    }
+
+                    #[test]
+                    fn one_for_zero_base_input_test(
+                        tick_current in tick_math::MIN_TICK..tick_math::MAX_TICK,
+                        amount_0 in 1000000..u64::MAX,
+                        amount_1 in 1000000..u64::MAX,
+                        tick_lower in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 100", |x| x % 10 == 0),
+                        tick_upper in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 100", |x| x % 10 == 0),
+                    ){
+                        let tick_spacing = 10;
+                        let zero_for_one = false;
+                        let is_base_input = true;
+                        if tick_lower%tick_spacing ==0 && tick_upper%tick_spacing ==0 && tick_current>tick_lower && tick_current<tick_upper{
+
+
+
+                            // println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper);
+                            let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state,  sum_amount_0, sum_amount_1) = setup_swap_test(
+                                tick_current,
+                                tick_spacing as u16,
+                                vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                zero_for_one
+                            );
+
+                            prop_assume!(sum_amount_0 > 1);
+                            let mut rng = rand::thread_rng();
+                            let amount_specified  = rng.gen_range(1..u64::MAX - sum_amount_1);
+
+                            let result = swap_internal(
+                                &amm_config,
+                                &mut pool_state.borrow_mut(),
+                                &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                &mut observation_state.borrow_mut(),
+                                &Some(bitmap_extension_state),
+                                amount_specified,
+                                tick_math::MAX_SQRT_PRICE_X64 - 1,
+                                zero_for_one,
+                                is_base_input,
+                                0,
+                            );
+
+
+                            if result.is_ok() {
+                                let ( amount_0_before, amount_1_before) = result.unwrap();
+
+                                let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state,  _sum_amount_0, _sum_amount_1) = setup_swap_test(
+                                    tick_current,
+                                    tick_spacing as u16,
+                                    vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                    zero_for_one
+                                );
+                                let result = swap_internal(
+                                    &amm_config,
+                                    &mut pool_state.borrow_mut(),
+                                    &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                    &mut observation_state.borrow_mut(),
+                                    &Some(bitmap_extension_state),
+                                    amount_specified,
+                                    tick_math::MAX_SQRT_PRICE_X64 - 1,
+                                    zero_for_one,
+                                    is_base_input,
+                                    oracle::block_timestamp_mock() as u32,
+                                );
+                                assert!(result.is_ok());
+
+                                // println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{},liquidity:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper, identity(pool_state.borrow().liquidity));
+
+                                    let (amount_0_after, amount_1_after) = result.unwrap();
+                                    assert_eq!(amount_0_before, amount_0_after);
+                                    assert_eq!(amount_1_before, amount_1_after);
+
+                            }else {
+                                let err =  result.err().unwrap();
+                                if err == crate::error::ErrorCode::MaxTokenOverflow.into(){
+                                    // println!("##### original swap is overflow ");
+                                    let _result = swap_internal(
+                                        &amm_config,
+                                        &mut pool_state.borrow_mut(),
+                                        &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                        &mut observation_state.borrow_mut(),
+                                        &Some(bitmap_extension_state),
+                                        amount_specified,
+                                        tick_math::MAX_SQRT_PRICE_X64 - 1,
+                                        zero_for_one,
+                                        is_base_input,
+                                        oracle::block_timestamp_mock() as u32,
+                                    );
+
+                                }else{
+                                    println!("{}", err);
+                                }
+                        }
+                    }
+                }
+
+
+                #[test]
+                fn one_for_zero_base_output_test(
+                    tick_current in tick_math::MIN_TICK..tick_math::MAX_TICK,
+                    amount_0 in 1000000..u64::MAX,
+                    amount_1 in 1000000..u64::MAX,
+                    tick_lower in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 100", |x| x % 10 == 0),
+                    tick_upper in (tick_math::MIN_TICK..=tick_math::MAX_TICK).prop_filter("Must be multiple of 100", |x| x % 10 == 0),
+                ){
+                    let tick_spacing = 10;
+                    let zero_for_one = false;
+                    let is_base_input = false;
+                    if tick_lower%tick_spacing ==0 && tick_upper%tick_spacing ==0 && tick_current>tick_lower && tick_current<tick_upper{
+
+
+                        // println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper);
+                        let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state,  sum_amount_0, _sum_amount_1) = setup_swap_test(
+                            tick_current,
+                            tick_spacing as u16,
+                            vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                            zero_for_one
+                        );
+                        prop_assume!(sum_amount_0 > 1);
+                        let mut rng = rand::thread_rng();
+                        let amount_specified  = rng.gen_range(1..sum_amount_0);
+
+                        let result = swap_internal(
+                            &amm_config,
+                            &mut pool_state.borrow_mut(),
+                            &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                            &mut observation_state.borrow_mut(),
+                            &Some(bitmap_extension_state),
+                            amount_specified,
+                            tick_math::MAX_SQRT_PRICE_X64 - 1,
+                            zero_for_one,
+                            is_base_input,
+                            0,
+                        );
+
+
+                        if result.is_ok() {
+                            let ( amount_0_before, amount_1_before) = result.unwrap();
+
+                            let (amm_config, pool_state, tick_array_states, observation_state,bitmap_extension_state,  _sum_amount_0, _sum_amount_1) = setup_swap_test(
+                                tick_current,
+                                tick_spacing as u16,
+                                vec![OpenPositionParam{amount_0:amount_0,amount_1:amount_1, tick_lower:tick_lower, tick_upper:tick_upper}],
+                                zero_for_one
+                            );
+                            let result = swap_internal(
+                                &amm_config,
+                                &mut pool_state.borrow_mut(),
+                                &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                &mut observation_state.borrow_mut(),
+                                &Some(bitmap_extension_state),
+                                amount_specified,
+                                tick_math::MAX_SQRT_PRICE_X64 - 1,
+                                zero_for_one,
+                                is_base_input,
+                                oracle::block_timestamp_mock() as u32,
+                            );
+                            assert!(result.is_ok());
+
+                                // println!("----- input: tick_current:{}, amount_0:{}, amount_1:{}, amount_specified:{},tick_lower:{}, tick_upper:{},liquidity:{}", tick_current, amount_0, amount_1,amount_specified, tick_lower, tick_upper, identity(pool_state.borrow().liquidity));
+
+                                let (amount_0_after, amount_1_after) = result.unwrap();
+                                assert_eq!(amount_0_before, amount_0_after);
+                                assert_eq!(amount_1_before, amount_1_after);
+
+                        }else {
+                            let err =  result.err().unwrap();
+                            if err == crate::error::ErrorCode::MaxTokenOverflow.into(){
+                                println!("##### original swap is overflow ");
+                                let _result = swap_internal(
+                                    &amm_config,
+                                    &mut pool_state.borrow_mut(),
+                                    &mut get_tick_array_states_mut(&tick_array_states).borrow_mut(),
+                                    &mut observation_state.borrow_mut(),
+                                    &Some(bitmap_extension_state),
+                                    amount_specified,
+                                    tick_math::MAX_SQRT_PRICE_X64 - 1,
+                                    zero_for_one,
+                                    is_base_input,
+                                    oracle::block_timestamp_mock() as u32,
+                                );
+                            }else{
+                                println!("{}", err);
+                            }
+                    }
+                }
+            }
+        }
+    }
 }
```

### programs/amm/src/instructions/swap_v2.rs
```diff
@@ -248,9 +248,14 @@ pub fn exact_internal_v2<'c: 'info, 'info>(
         amount_0_without_fee = amount_0.checked_sub(transfer_fee_0).unwrap();
         amount_1_without_fee = amount_1;
         let (transfer_amount_0, transfer_amount_1) = (amount_0, amount_1 + transfer_fee_1);
-
-        msg!("amount_0:{}, transfer_fee_0:{}", amount_0, transfer_fee_0);
-        msg!("amount_1:{}, transfer_fee_1:{}", amount_1, transfer_fee_1);
+        #[cfg(feature = "enable-log")]
+        msg!(
+            "amount_0:{}, transfer_fee_0:{}, amount_1:{}, transfer_fee_1:{}",
+            amount_0,
+            transfer_fee_0,
+            amount_1,
+            transfer_fee_1
+        );
         transfer_from_user_to_pool_vault(
             &ctx.payer,
             &token_account_1,
```

### programs/amm/src/instructions/update_reward_info.rs
```diff
@@ -13,7 +13,8 @@ pub fn update_reward_infos<'a, 'b, 'c, 'info>(
 ) -> Result<()> {
     let clock = Clock::get()?;
     let mut pool_state = ctx.accounts.pool_state.load_mut()?;
-    let updated_reward_infos = pool_state.update_reward_infos(u64::try_from(clock.unix_timestamp).unwrap())?;
+    let updated_reward_infos =
+        pool_state.update_reward_infos(u64::try_from(clock.unix_timestamp).unwrap())?;
 
     emit!(UpdateRewardInfosEvent {
         reward_growth_global_x64: RewardInfo::get_reward_growths(&updated_reward_infos)
```

### programs/amm/src/libraries/big_num.rs
```diff
@@ -10,6 +10,10 @@ construct_uint! {
     pub struct U256(4);
 }
 
+construct_uint! {
+    pub struct U512(8);
+}
+
 #[macro_export]
 macro_rules! construct_bignum {
     ( $(#[$attr:meta])* $visibility:vis struct $name:ident ( $n_words:tt ); ) => {
@@ -335,11 +339,6 @@ macro_rules! construct_bignum {
         }
     };
 }
-
-construct_bignum! {
-    pub struct U512(8);
-}
-
 construct_bignum! {
     pub struct U1024(16);
 }
```

### programs/amm/src/libraries/full_math.rs
```diff
@@ -3,7 +3,7 @@
 //! and supports U128 operations.
 //!
 
-use crate::libraries::big_num::{U128, U256};
+use crate::libraries::big_num::{U128, U256, U512};
 
 /// Trait for calculating `val * num / denom` with different rounding modes and overflow
 /// protection.
@@ -83,26 +83,46 @@ pub trait MulDiv<RHS = Self> {
     fn to_underflow_u64(self) -> u64;
 }
 
-pub trait Upcast {
+pub trait Upcast256 {
     fn as_u256(self) -> U256;
 }
-impl Upcast for U128 {
+impl Upcast256 for U128 {
     fn as_u256(self) -> U256 {
         U256([self.0[0], self.0[1], 0, 0])
     }
 }
 
-pub trait Downcast {
+pub trait Downcast256 {
     /// Unsafe cast to U128
     /// Bits beyond the 128th position are lost
     fn as_u128(self) -> U128;
 }
-impl Downcast for U256 {
+impl Downcast256 for U256 {
     fn as_u128(self) -> U128 {
         U128([self.0[0], self.0[1]])
     }
 }
 
+pub trait Upcast512 {
+    fn as_u512(self) -> U512;
+}
+impl Upcast512 for U256 {
+    fn as_u512(self) -> U512 {
+        U512([self.0[0], self.0[1], self.0[2], self.0[3], 0, 0, 0, 0])
+    }
+}
+
+pub trait Downcast512 {
+    /// Unsafe cast to U256
+    /// Bits beyond the 256th position are lost
+    fn as_u256(self) -> U256;
+}
+impl Downcast512 for U512 {
+    fn as_u256(self) -> U256 {
+        U256([self.0[0], self.0[1], self.0[2], self.0[3]])
+    }
+}
+
 impl MulDiv for u64 {
     type Output = u64;
 
@@ -168,21 +188,21 @@ impl MulDiv for U256 {
 
     fn mul_div_floor(self, num: Self, denom: Self) -> Option<Self::Output> {
         assert_ne!(denom, U256::default());
-        let r = (self * num) / denom;
-        if r > U128::MAX.as_u256() {
+        let r = (self.as_u512() * num.as_u512()) / denom.as_u512();
+        if r > U256::MAX.as_u512() {
             None
         } else {
-            Some(r)
+            Some(r.as_u256())
         }
     }
 
     fn mul_div_ceil(self, num: Self, denom: Self) -> Option<Self::Output> {
         assert_ne!(denom, U256::default());
-        let r = (self * num + (denom - 1)) / denom;
-        if r > U128::MAX.as_u256() {
+        let r = (self.as_u512() * num.as_u512() + (denom - 1).as_u512()) / denom.as_u512();
+        if r > U256::MAX.as_u512() {
             None
         } else {
-            Some(r)
+            Some(r.as_u256())
         }
     }
 
```

### programs/amm/src/libraries/liquidity_math.rs
```diff
@@ -168,7 +168,7 @@ pub fn get_delta_amount_0_unsigned(
     mut sqrt_ratio_b_x64: u128,
     liquidity: u128,
     round_up: bool,
-) -> u64 {
+) -> Result<u64> {
     // sqrt_ratio_a_x64 should hold the smaller value
     if sqrt_ratio_a_x64 > sqrt_ratio_b_x64 {
         std::mem::swap(&mut sqrt_ratio_a_x64, &mut sqrt_ratio_b_x64);
@@ -179,21 +179,23 @@ pub fn get_delta_amount_0_unsigned(
 
     assert!(sqrt_ratio_a_x64 > 0);
 
-    if round_up {
+    let result = if round_up {
         U256::div_rounding_up(
             numerator_1
                 .mul_div_ceil(numerator_2, U256::from(sqrt_ratio_b_x64))
                 .unwrap(),
             U256::from(sqrt_ratio_a_x64),
         )
-        .as_u64()
     } else {
-        (numerator_1
+        numerator_1
             .mul_div_floor(numerator_2, U256::from(sqrt_ratio_b_x64))
             .unwrap()
-            / U256::from(sqrt_ratio_a_x64))
-        .as_u64()
+            / U256::from(sqrt_ratio_a_x64)
+    };
+    if result > U256::from(u64::MAX) {
+        return Err(ErrorCode::MaxTokenOverflow.into());
     }
+    return Ok(result.as_u64());
 }
 
 /// Gets the delta amount_1 for given liquidity and price range
@@ -203,13 +205,13 @@ pub fn get_delta_amount_1_unsigned(
     mut sqrt_ratio_b_x64: u128,
     liquidity: u128,
     round_up: bool,
-) -> u64 {
+) -> Result<u64> {
     // sqrt_ratio_a_x64 should hold the smaller value
     if sqrt_ratio_a_x64 > sqrt_ratio_b_x64 {
         std::mem::swap(&mut sqrt_ratio_a_x64, &mut sqrt_ratio_b_x64);
     };
 
-    if round_up {
+    let result = if round_up {
         U256::from(liquidity).mul_div_ceil(
             U256::from(sqrt_ratio_b_x64 - sqrt_ratio_a_x64),
             U256::from(fixed_point_64::Q64),
@@ -220,16 +222,19 @@ pub fn get_delta_amount_1_unsigned(
             U256::from(fixed_point_64::Q64),
         )
     }
-    .unwrap()
-    .as_u64()
+    .unwrap();
+    if result > U256::from(u64::MAX) {
+        return Err(ErrorCode::MaxTokenOverflow.into());
+    }
+    return Ok(result.as_u64());
 }
 
 /// Helper function to get signed delta amount_0 for given liquidity and price range
 pub fn get_delta_amount_0_signed(
     sqrt_ratio_a_x64: u128,
     sqrt_ratio_b_x64: u128,
     liquidity: i128,
-) -> u64 {
+) -> Result<u64> {
     if liquidity < 0 {
         get_delta_amount_0_unsigned(
             sqrt_ratio_a_x64,
@@ -252,7 +257,7 @@ pub fn get_delta_amount_1_signed(
     sqrt_ratio_a_x64: u128,
     sqrt_ratio_b_x64: u128,
     liquidity: i128,
-) -> u64 {
+) -> Result<u64> {
     if liquidity < 0 {
         get_delta_amount_1_unsigned(
             sqrt_ratio_a_x64,
@@ -284,41 +289,28 @@ pub fn get_delta_amounts_signed(
             tick_math::get_sqrt_price_at_tick(tick_lower)?,
             tick_math::get_sqrt_price_at_tick(tick_upper)?,
             liquidity_delta,
-        );
+        )
+        .unwrap();
     } else if tick_current < tick_upper {
         amount_0 = get_delta_amount_0_signed(
             sqrt_price_x64_current,
             tick_math::get_sqrt_price_at_tick(tick_upper)?,
             liquidity_delta,
-        );
+        )
+        .unwrap();
         amount_1 = get_delta_amount_1_signed(
             tick_math::get_sqrt_price_at_tick(tick_lower)?,
             sqrt_price_x64_current,
             liquidity_delta,
-        );
+        )
+        .unwrap();
     } else {
         amount_1 = get_delta_amount_1_signed(
             tick_math::get_sqrt_price_at_tick(tick_lower)?,
             tick_math::get_sqrt_price_at_tick(tick_upper)?,
             liquidity_delta,
-        );
+        )
+        .unwrap();
     }
     Ok((amount_0, amount_1))
 }
-
-#[cfg(test)]
-mod liquidity_math_test {
-    use super::*;
-    mod get_amounts_delta_signed {
-        use super::*;
-
-        #[test]
-        fn get_amounts_delta_signed_test() {
-            let current_tick = -1860;
-            let current_price = tick_math::get_sqrt_price_at_tick(current_tick).unwrap();
-            let (amount0, amount1) =
-                get_delta_amounts_signed(current_tick, current_price, -6960, 4080, 100000).unwrap();
-            println!("amount0:{}, amount1:{}", amount0, amount1)
-        }
-    }
-}
```

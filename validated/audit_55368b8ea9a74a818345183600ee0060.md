The HarfBuzz CVE (BIT-java-2023-25193 / CVE-2023-25193) concerns O(n²) growth from consecutive mark-glyph attachment lookback in a text-shaping engine. This bug class requires text/font glyph processing with unbounded backward iteration over attacker-controlled "marks" — a construct with no analog in this Solana AMM program.

The raydium-amm codebase contains no font/glyph/text-shaping logic, no unbounded loops driven by attacker-controlled sequential mark data, and no lookback iteration patterns resembling `hb-ot-layout-gsubgpos.hh`. The reachable in-scope surfaces (`Initialize2`, `Deposit`, `Withdraw`, the swap instructions in `program/src/processor.rs`, PDA/account checks, `AmmInfo`/`TargetOrders` loading, and `Calculator` math in `program/src/math.rs`) all operate on fixed, small numbers of accounts and O(1) arithmetic per instruction — there is no per-transaction data structure that grows quadratically based on user input length like HarfBuzz's mark sequence. [1](#0-0) [2](#0-1) 

#No vulnerability found for this question.

### Citations

**File:** program/src/processor.rs (L2816-2863)
```rust
    /// Processes `process_withdraw_excess_lamports` instruction.
    pub fn process_withdraw_excess_lamports(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        let collect_lamports_info = next_account_info(account_info_iter)?;
        let amm_authority_info = next_account_info(account_info_iter)?;
        let token_program_info = next_account_info(account_info_iter)?;
        if !collect_lamports_info.is_signer
            || config_feature::collect_lamports::id() != *collect_lamports_info.key
        {
            return Err(AmmError::InvalidSignAccount.into());
        }
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let authority = Self::authority_id(program_id, AUTHORITY_AMM, 254u8)?;
        check_assert_eq!(
            *amm_authority_info.key,
            authority,
            "authority",
            AmmError::InvalidProgramAddress
        );
        while account_info_iter.len() != 0 {
            let source_account_info = next_account_info(account_info_iter)?;
            if *source_account_info.owner == spl_token::id() {
                Self::withdraw_excess_lamports_from_token(
                    token_program_info,
                    source_account_info,
                    collect_lamports_info,
                    amm_authority_info,
                    AUTHORITY_AMM,
                    254u8,
                )?;
            } else if source_account_info.owner == program_id {
                Self::withdraw_excess_lamports_from_program(
                    source_account_info,
                    collect_lamports_info,
                )?;
            } else {
                continue;
            }
        }
        return Ok(());
```

**File:** program/src/math.rs (L41-78)
```rust
impl Calculator {
    pub fn to_u128(val: u64) -> Result<u128, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }

    pub fn to_u64(val: u128) -> Result<u64, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }

    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }

    // out: 0, 1, 2, 3, 5, 8, 13, 21, 34, 55
    pub fn fibonacci(order_num: u64) -> Vec<u64> {
        let mut fb = Vec::new();
        for i in 0..order_num {
            if i == 0 {
                fb.push(0u64);
            } else if i == 1 {
                fb.push(1u64);
            } else if i == 2 {
                fb.push(2u64);
            } else {
                let ret = fb[(i - 1u64) as usize] + fb[(i - 2u64) as usize];
                fb.push(ret);
            };
        }
        return fb;
    }
```

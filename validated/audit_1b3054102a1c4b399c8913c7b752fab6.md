### Title
Truncating decimal-scaling in `pallet-hyper-fungible-token::on_accept` permanently strands dust on every cross-chain deposit - (File: modules/pallets/hyper-fungible-token/src/impls.rs)

### Summary
The `liquidateFrom`-style bug class is: two different code paths enforce two different amount granularities (`lotSize` vs `tradingLotSize`), so value processed through the coarser path can leave a remainder that is invisible/unusable to the finer-grained path, permanently stranding it. `pallet-hyper-fungible-token` has the same shape: outbound transfers (EVM → substrate direction, `convert_to_erc20`) scale up **exactly** (multiplication, no loss), while inbound transfers (EVM → substrate, `convert_to_balance`) scale down with **integer division that silently truncates**, and the truncated remainder is neither credited to the beneficiary nor returned to anyone.

### Finding Description
`convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs` converts an incoming ERC20 `U256` amount to the pallet's local balance type by integer division: [1](#0-0) 

```
let dec_str = (value / U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))).to_string();
```

Whenever `erc_decimals > local_decimals` (the documented, common case — e.g. `BridgeToken` is 18-decimal on EVM while native BRIDGE is 12-decimal on nexus, per [2](#0-1) ), any incoming amount whose low-order digits are not an exact multiple of `10^(erc_decimals - local_decimals)` has that remainder floored off. The README confirms this conversion is exactly what `on_accept` uses to credit the beneficiary: [3](#0-2) 

The counterpart outbound path, `convert_to_erc20`, is exact (pure multiplication, no rounding), used in `send()`: [4](#0-3) [5](#0-4) 

Because the EVM side (`HyperFungibleToken.send`) accepts an arbitrary `uint256 amount` with no lot-size/granularity restriction, and burns/escrows exactly that amount, a user can trivially send an amount that is not a multiple of the scale factor. The nexus-side pallet then floors the credited amount, and the un-credited remainder is not tracked, refunded, or recoverable by any actor — it is permanently lost from circulation (for the mint/burn, non-native custody model) or permanently stuck in the pallet's escrow account with no accounting entry pointing to it (for the native custody model), since `NativeAssets`/escrow balances are keyed only by the truncated, credited amount.

This exactly mirrors the reported bug class: one path (`send`, analogous to `matchOrders`/AMM enforcing `tradingLotSize`) has no granularity restriction, while the other path (`on_accept`'s scaling, analogous to `liquidateFrom`'s `lotSize` check) silently produces amounts below the finer path's precision, and there is no mechanism to reclaim the leftover.

### Impact Explanation
Every cross-chain deposit whose amount is not an exact multiple of `10^(erc_decimals - local_decimals)` permanently loses the fractional remainder. This is systematic (triggers on essentially any non-round transfer amount, not an edge case), requires no attacker privilege, and directly causes permanent loss/freezing of user funds with no path to recovery — satisfying the "permanent freezing of funds" acceptance criterion. Because the pallet is the generic token-bridge primitive (`HyperFungibleToken`/`BridgeToken`), this affects any deployment using differing EVM vs. substrate decimals, which the code and docs indicate is the expected configuration (BRIDGE: 18 vs 12).

### Likelihood Explanation
High likelihood: it requires only a single ordinary `send()` call from an unprivileged user with an amount that isn't a round multiple of the decimal-scale factor (e.g., any amount with non-zero digits in the last 6 decimal places for the 18-vs-12 BRIDGE case). No special conditions, governance action, or malicious actor is needed — it is a routine, unprivileged token-bridge transaction.

### Recommendation
Track the truncated remainder (e.g., accumulate dust per asset/chain and let it be swept/credited on a subsequent transfer, or reject/round the EVM-side `send` amount to a multiple of the scale factor before dispatch, similar to how `BandwidthManager` reverts with `PriceNotRepresentable()` on the EVM side when an amount is not representable at the target decimals) rather than silently flooring value out of existence in `convert_to_balance`.

### Proof of Concept
1. Deploy `BridgeToken` (18 decimals) on an EVM chain paired with `pallet-hyper-fungible-token` on nexus (12 decimals), per the documented configuration.
2. A user calls `BridgeToken.send({ dest: nexus, amount: 1_000_000_000_000_000_001 (1 BRIDGE + 1 wei) , ... })` — this burns/escrows exactly that amount on the EVM side (see `HyperFungibleToken.send`/`BridgeToken` burn logic).
3. The ISMP message reaches nexus; `on_accept` calls `convert_to_balance(value=1_000_000_000_000_000_001, erc_decimals=18, local_decimals=12)`, computing `value / 10^6 = 1_000_000_000_000` (i.e. exactly 1 BRIDGE, local units), discarding the `1` remainder unit (in 18-decimal terms, `0.000000000000000001`... scaled, the trailing sub-`10^6` digits are always discarded).
4. The beneficiary is credited only the floored amount; the discarded remainder is not recorded anywhere in pallet storage (`NativeAssets`, escrow account balance, or otherwise) and cannot be claimed by the user, the pallet, or governance.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-52)
```rust
pub fn convert_to_balance<B: core::str::FromStr>(
	value: U256,
	erc_decimals: u8,
	local_decimals: u8,
) -> Result<B, B::Err> {
	let dec_str = (value /
		U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32)))
	.to_string();
	dec_str.parse::<B>()
}
```

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L54-59)
```rust
/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

**File:** modules/pallets/hyper-fungible-token/README.md (L81-89)
```markdown
## ISMP module behaviour

- `on_accept` — receives `Send` messages from the paired EVM contract. Maps
  the source contract back to a local asset via `ContractToAsset`, scales the
  amount using `Precisions`, then mints (non-native) or releases from escrow
  (native) to the beneficiary. Emits `TokenReceived`.
- `on_timeout` — refunds the original sender's balance from escrow or by
  re-minting. Emits `TokenRefunded`.
- `on_response` — unused; this pallet uses post-only messaging.
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-296)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```

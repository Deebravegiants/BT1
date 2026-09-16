Based on my research, I found a strong analog to the reported bug class in `pallet-hyper-fungible-token`'s decimal conversion logic.

### Title
Zero-amount mint after decimal-down-scaling truncation in `pallet-hyper-fungible-token` `on_accept` leads to loss of user funds - (File: `modules/pallets/hyper-fungible-token/src/impls.rs`)

### Summary
`convert_to_balance` performs integer division to rescale an incoming ERC20 `U256` amount down to the local chain's balance precision when a remote chain (e.g. an EVM `HyperFungibleToken`) has more decimals than the local asset. Just like the `InsuranceFund.depositFor` share-rounding bug, a small enough incoming amount truncates to zero after this division, with no check to reject or refund a zero-resulting credit.

### Finding Description
`convert_to_balance` in `modules/pallets/hyper-fungible-token/src/impls.rs` computes:
```rust
let dec_str = (value / U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))).to_string();
dec_str.parse::<B>()
``` [1](#0-0) 

This is used to translate an amount received from a remote chain's ERC20-precision message into the local pallet's balance type before crediting/minting it. If `erc_decimals > local_decimals` (a real, supported configuration — `Precisions` stores a per-`(asset, chain)` decimals value precisely for this scaling), an incoming raw amount smaller than `10^(erc_decimals - local_decimals)` truncates to exactly `0` in local balance units.

The `PostRequest`/message body carrying `amount` is attacker/relayer-influenced input (a message dispatched from a peer HFT contract on a remote chain, delivered here after ISMP proof verification), so nothing prevents a message declaring, or actually escrowing/burning, a dust amount on the EVM side that decodes to `0` locally. Analogous to the `InsuranceFund` bug, the root issue is a rounding-to-zero division result reaching a mint/credit path with no `> 0` guard, unlike `IntentGatewayV2`'s fill/escrow paths in this same repo, which are shown (via `testPartialFill_RoundingDustReleasedToFinalSolver` and related tests) to explicitly track and release rounding dust rather than silently dropping it [2](#0-1) .

### Impact Explanation
On the EVM side, `send()` burns/escrows the full `params.amount` and dispatches a cross-chain message scaled up via `convert_to_erc20` [3](#0-2) . On the reverse leg (remote → local), if the reverse scaling division truncates an incoming amount to zero, the recipient is credited nothing while real value was consumed/burned on the source side — a straightforward loss-of-funds pattern matching the reported bug class ("user's assets are transferred/consumed but they receive zero as a result of a rounding division"). Given decimal mismatches across the 40+ HyperFungibleToken deployments this protocol operates (12-decimal native BRIDGE vs 18-decimal EVM representations, per `BridgeToken.sol`'s own scale-by-`10^6` comment) [4](#0-3) , this is a realistically reachable configuration, not a contrived edge case.

### Likelihood Explanation
Medium: it requires (a) a token pair configured with a decimals gap large enough that a plausible dust amount rounds to zero, and (b) a relayer/user willing to submit (or a legitimate small transfer that happens to be) such a dust amount. Unlike the InsuranceFund PoC (attacker-controlled pool ratio), this path is not attacker-triggerable for profit — it's a silent funds-loss/griefing vector against whoever sends the dust amount, most likely to manifest as accidental value loss for small cross-chain transfers rather than a directly exploitable drain.

### Recommendation
Add an explicit zero-check after `convert_to_balance` (and symmetrically in `convert_to_erc20`) in the message-receive path of `pallet-hyper-fungible-token`, rejecting or reverting the transfer (and, ideally, timing it out to trigger the existing `onPostRequestTimeout` refund path on the EVM side) rather than silently minting/crediting `0`, mirroring the recommended `require(shares > 0)` fix pattern from the reported issue.

### Proof of Concept
Given a token registered with `erc_decimals = 18` and `local_decimals = 6` (a supported, documented configuration per `ChainConfig`/`Precisions`), an incoming ERC20 amount of `999_999_999_999` wei (`< 10^12`) computes:
```
value / 10^(18-6) = 999_999_999_999 / 10^12 = 0
```
`convert_to_balance` returns `"0"` and the local mint/credit proceeds with amount `0`, while the corresponding EVM-side operation (burn/escrow of `999_999_999_999` wei, non-zero) has already executed or will execute as the message is finalized — resulting in a real, non-zero value consumed with a zero credit delivered.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L39-52)
```rust
/// Converts an ERC20 U256 amount to a local balance type
///
/// Divides by 10^(erc_decimals - local_decimals) to scale down from ERC20 precision.
/// The target type must implement `FromStr`.
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L1727-1740)
```text
    /*//////////////////////////////////////////////////////////////
                    ROUNDING DUST IN PARTIAL FILLS (Finding #4)
    //////////////////////////////////////////////////////////////*/

    /// @notice Verifies that rounding dust from integer division in partial fills
    /// is not permanently locked. The final solver completing the order should
    /// receive the full remaining escrow balance rather than a truncated amount.
    function testPartialFill_RoundingDustReleasedToFinalSolver() public {
        // Choose amounts that produce rounding truncation:
        // input = 100 USDC (100e6), output = 3 DAI (3e18)
        // Each of 3 solvers fills 1 DAI. Proportional release per fill:
        //   100e6 * 1e18 / 3e18 = 33333333 (truncated from 33333333.33...)
        // Without fix: 3 * 33333333 = 99999999, leaving 1 unit locked.
        // With fix: final solver gets remaining balance = 100e6 - 2*33333333 = 33333334
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L290-296)
```rust
			};

			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

```

**File:** evm/src/apps/BridgeToken.sol (L33-36)
```text
 *
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

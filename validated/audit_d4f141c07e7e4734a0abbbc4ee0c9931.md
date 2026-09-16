### Title
Under-collateralization of `WrappedHyperFungibleToken` locked balance is unrecoverable and breaks the cross-chain 1:1 peg — ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken` is the home-chain custody contract for the Hyper Fungible Token bridge: it locks the canonical ERC20 supply on `send()` and unlocks it on `onAccept()`, while paired `HyperFungibleToken` deployments on every other chain burn/mint 1:1 against that locked balance [1](#0-0) . Like frxETH's assumption that 32 ETH always backs a validator, this design assumes the wrapper's on-chain balance always equals `amount` moved by `safeTransferFrom`/`safeTransfer`. There is no mechanism to detect or remediate a shortfall between the locked balance and total minted supply elsewhere, exactly the class of risk the frxETH report flags — an external, uncontrollable reduction in backing collateral with no protocol-level repeg/burn logic.

### Finding Description
`send()` locks tokens with `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` and encodes `params.amount` verbatim into the cross-chain `Message`, which is what `HyperFungibleToken` on remote chains mints [2](#0-1) . On receipt of an inbound message, `onAccept()` releases exactly `message.amount` via `safeTransfer` [3](#0-2) . The contract never checks the actual balance delta before/after transfer, and never reconciles the locked balance against total supply minted across remote `HyperFungibleToken` deployments.

If the underlying token's balance in the wrapper can fall below the amount that was recorded as locked — via a fee-on-transfer/deflationary token, a rebasing token that can decrease (the direct analog of ETH "slashing" reducing backing), or any other external mechanism that reduces the custodied balance without a corresponding burn message being sent — the wrapper becomes under-collateralized. The `native = true` custody model has the identical assumption for `pallet-hyper-fungible-token`'s substrate-side escrow, which also locks/unlocks 1:1 with no supply reconciliation [4](#0-3) .

Exactly as the frxETH report notes for ETH 2.0 slashing, there is no built-in mechanism to (a) detect the shortfall, (b) burn outstanding remote supply to restore the peg, or (c) determine who is responsible for topping up the collateral. Once the shortfall exists, the last users to attempt a bridge-back (`onAccept` unlock) will find the wrapper unable to fully pay out, and earlier withdrawers effectively drain the remaining backing first — a race that permanently strands the last holders' minted tokens.

### Impact Explanation
This is a permanent freezing of funds / unbacked-mint scenario: remote `HyperFungibleToken` supply continues to be treated as fully redeemable 1:1, but the home-chain collateral pool can silently fall short. Because there is no accounting check, no circuit breaker, and no on-chain mechanism to burn/adjust remote supply in response to a collateral shortfall, once a shortfall exists it is undetectable until users attempt to redeem and some transactions fail or drain the pool for stragglers, matching the "asset-backed guarantee isn't without risk" finding from the referenced report, but here it applies to the bridge's collateral rather than only the underlying token's own risk profile.

### Likelihood Explanation
This requires the underlying wrapped ERC20 to be a non-standard token (fee-on-transfer, deflationary/rebasing-down, or otherwise able to reduce the wrapper's held balance independent of `send`/`onAccept` calls). This is a deployment/token-selection risk rather than an implementation flaw exploitable by an unprivileged attacker on a straightforward ERC20 deployment — the protocol's documentation does not restrict `WrappedHyperFungibleToken` to strictly-standard ERC20s, so an integrator wrapping a rebasing or fee-on-transfer token would silently introduce this risk.

### Recommendation
Add balance-delta checks around `safeTransferFrom`/`safeTransfer` in `send()`/`onAccept()` to detect actual amounts moved rather than trusting `params.amount`/`message.amount`, and reject or scale messages accordingly. Track the wrapper's total minted-elsewhere supply against its actual locked balance, and provide a governance/pause mechanism (mirroring the existing `Pausable` hooks) that freezes new mints once a collateral shortfall is detected, similar to the mitigation FortisFortuna described for frxETH (either subsidize the shortfall or explicitly allow the peg to float with clear on-chain signaling).

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` on the home chain wrapping a fee-on-transfer or negative-rebasing ERC20.
2. User calls `send()` with `amount = 100`; `safeTransferFrom` is invoked for `100`, but due to a transfer fee/rebase the wrapper's actual balance only increases by `98`.
3. The dispatched `Message.amount` is still `100`, so the paired `HyperFungibleToken` on the remote chain mints `100` tokens — 2 tokens are now unbacked.
4. Repeated over multiple `send()` calls (or a single large negative rebase event on the underlying), the wrapper's real balance falls further behind total remote-minted supply.
5. When remote holders bridge back (`onAccept()` triggers `safeTransfer`), the wrapper eventually cannot fully pay all claims — later `onAccept()` calls revert or drain remaining balance, leaving some users permanently unable to redeem, exactly mirroring the frxETH slashing scenario where validator balance can no longer back all pegged tokens.

### Citations

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L10-12)
```text
## Architecture

The typical deployment uses a `WrappedHyperFungibleToken` on the token's home chain and a `HyperFungibleToken` on every remote chain. This keeps canonical supply on the home chain — the WrappedHFT accumulates locked tokens as users bridge out and releases them when users bridge back.
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-290)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-324)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L257-290)
```rust
			// Lock or burn the local asset
			let decimals = if params.asset_id == T::NativeAssetId::get() {
				// escrow the native asset
				<T as Config>::NativeCurrency::transfer(
					&who,
					&Self::pallet_account(),
					params.amount,
					ExistenceRequirement::AllowDeath,
				)?;
				T::Decimals::get()
			} else {
				let is_native = NativeAssets::<T>::get(params.asset_id.clone());
				if is_native {
					<T as Config>::Assets::transfer(
						params.asset_id.clone(),
						&who,
						&Self::pallet_account(),
						params.amount.into(),
						Preservation::Expendable,
					)?;
				} else {
					<T as Config>::Assets::burn_from(
						params.asset_id.clone(),
						&who,
						params.amount.into(),
						Preservation::Expendable,
						Precision::Exact,
						Fortitude::Polite,
					)?;
				}
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					params.asset_id.clone(),
				)
			};
```

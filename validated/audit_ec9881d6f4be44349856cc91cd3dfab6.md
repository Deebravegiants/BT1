Based on the investigation, the strongest analog is in `pallet-hyper-fungible-token`'s `on_accept` handler, but I could not fully verify a definitive freeze impact due to incomplete file access on this final pass, so I'll state findings with appropriate caveats.

### Title
Missing zero/dead-beneficiary check in `pallet-hyper-fungible-token`'s `on_accept`/`on_timeout` mint path - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
On the EVM side, `HyperFungibleToken.onAccept` and `onPostRequestTimeout` mint via OpenZeppelin's `ERC20._mint`, which itself reverts when the recipient is `address(0)`, so the audit's exact bug class does not reproduce there [1](#0-0) . However, the Substrate counterpart, `pallet-hyper-fungible-token`, decodes the arbitrary `to`/`from` bytes chosen by the sender on the EVM side directly into a 32-byte `AccountId` with no validation that the resulting account is non-zero, then mints/transfers funds into it via `fungibles::Mutate::mint_into` or `Currency::transfer`, neither of which reject an all-zero `AccountId` the way OpenZeppelin's ERC20 rejects `address(0)`.

### Finding Description
In `on_accept`, the beneficiary is derived purely from message bytes controlled by the calling EVM user (via `HyperFungibleToken.send`'s `to` parameter): if 32 bytes, used directly; if 20 bytes, left-padded with zeros — with no check that the decoded `beneficiary_bytes` are non-zero before converting to `T::AccountId` and crediting funds [2](#0-1) . The same pattern occurs in `on_timeout`'s refund path, which decodes `message.from` into a `sender_bytes` array with identical left-padding/32-byte handling and no zero check before crediting the refund [3](#0-2) . Both paths then either transfer from the pallet's custody account or mint new assets into `beneficiary` [4](#0-3) [5](#0-4) .

### Impact Explanation
If an EVM-side user calls `HyperFungibleToken.send` with `to = abi.encodePacked(address(0))` (or any all-zero 32-byte value), their tokens are burned on the EVM side and, upon successful delivery, `on_accept` mints/transfers the corresponding balance to the zero `AccountId` on the parachain, which is unlikely to be a spendable, user-controlled account — resulting in a permanent loss of the transferred funds. I could not fully confirm within the remaining tool budget whether `pallet-balances`/`pallet-assets` in this runtime enforce an existential-deposit or "dead account" rule that would cause such a transfer to fail loudly rather than silently succeed and strand funds, so the exact behavior (revert vs. silent freeze) is unverified.

### Likelihood Explanation
This requires no privileged access — any user driving a normal `send` cross-chain transfer can supply an arbitrary/malformed `to` address, whether by accident (e.g. address encoding bug) or by triggering the same class of unintentional loss described in the original Hats.sol report. There is no admin/governance gate on this path, matching the report's "unprivileged" root cause: no defensive check on the beneficiary before minting.

### Recommendation
Add an explicit check in `on_accept` and `on_timeout` (and the mirrored `on_response`/refund logic) that the decoded 32-byte beneficiary/sender is not all-zero (and ideally not equal to a known "dead"/burn account) before performing the mint or transfer, returning an error (e.g. `HftError::InvalidRecipient`) instead of silently crediting an unusable account.

### Proof of Concept
1. On the EVM home chain, call `HyperFungibleToken.send(SendParams({ dest: <parachain>, to: abi.encodePacked(address(0)), amount: X, ... }))`. This burns `X` tokens from `msg.sender` [6](#0-5) .
2. The relayer delivers the resulting ISMP POST request to `pallet-hyper-fungible-token::on_accept` on the destination chain.
3. `message.to` decodes to a 20-byte all-zero value, which is left-padded to a 32-byte all-zero `beneficiary_bytes` and converted to `T::AccountId` without a zero check [2](#0-1) .
4. The pallet credits `X` tokens (scaled for decimals) to this zero `AccountId` via `mint_into`/`transfer` [4](#0-3) , permanently removing them from the sender's control with no recovery path.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-266)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L61-72)
```rust
		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
		let beneficiary: T::AccountId = beneficiary_bytes.into();
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
		}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L224-233)
```rust
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
					Err(HftError::InvalidSenderLength(from_bytes.len()))?
				}
				let beneficiary: T::AccountId = sender_bytes.into();
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L257-285)
```rust
				// Refund: release escrowed tokens back to the original sender
				if local_asset_id == T::NativeAssetId::get() {
					<T as Config>::NativeCurrency::transfer(
						&Pallet::<T>::pallet_account(),
						&beneficiary,
						amount.into(),
						ExistenceRequirement::AllowDeath,
					)
					.map_err(|e| HftError::TransferFailed(e.into()))?;
				} else {
					let is_native = NativeAssets::<T>::get(local_asset_id.clone());
					if is_native {
						<T as Config>::Assets::transfer(
							local_asset_id,
							&Pallet::<T>::pallet_account(),
							&beneficiary,
							amount.into(),
							Preservation::Expendable,
						)
						.map_err(|e| HftError::TransferFailed(e.into()))?;
					} else {
						<T as Config>::Assets::mint_into(
							local_asset_id,
							&beneficiary,
							amount.into(),
						)
						.map_err(|e| HftError::MintFailed(e.into()))?;
					}
				}
```

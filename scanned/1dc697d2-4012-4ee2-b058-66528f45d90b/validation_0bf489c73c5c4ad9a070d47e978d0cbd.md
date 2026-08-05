No vulnerability found for this question.

Based on my investigation, the REW-1 issue is specific to a Solidity `WETH9`-style `withdrawTo` function whose availability differs across EVM chains (Arbitrum vs. Avalanche C-Chain). This is a chain-incompatibility issue tied to third-party ERC20/WETH contract implementations deployed by an application (GMX) on top of an EVM, not to the underlying chain's core protocol.

I searched the polkadot-sdk repository for analogous patterns:
- No `withdrawTo`/`withdraw_to` usage exists tied to a native-token-unwrap-and-forward pattern; the only `withdraw_to` matches are in `pallet-asset-conversion` (liquidity pool withdrawals), which is functionally unrelated [1](#0-0) .
- `pallet-revive` (the EVM-compatibility pallet) implements its own precompile framework where unsupported precompiles explicitly and safely fail with `UnsupportedPrecompileAddress` rather than silently behaving differently per-chain, e.g. the `PointEval` precompile [2](#0-1) .
- `pallet-revive` is designed to be runtime-agnostic: chain-specific parameters like `ChainId`, `NativeToEthRatio`, and `Precompiles` are explicit `Config` items set per-runtime (e.g. `substrate/bin/node/runtime/src/lib.rs` vs `cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs`), so there is no hidden native-token-unwrap primitive whose support silently varies by deployment target [3](#0-2) [4](#0-3) .

The core root cause of REW-1 — a hardcoded call to a chain-specific WETH function that silently doesn't exist on other deployment targets — does not have a structural analog in FRAME/Substrate's pallet configuration model, XCM, or `pallet-revive`'s precompile framework, all of which require explicit, compile-time-checked configuration per runtime rather than implicit assumptions about environment-specific contract behavior.

### Citations

**File:** substrate/frame/asset-conversion/src/lib.rs (L1-1)
```rust
// This file is part of Substrate.
```

**File:** substrate/frame/revive/src/precompiles/builtin/point_eval.rs (L33-41)
```rust
	fn call(
		_address: &[u8; 20],
		_input: Vec<u8>,
		_env: &mut impl Ext<T = Self::T>,
	) -> Result<Vec<u8>, Error> {
		// Exists on Ethereum but we didn't implement it, yet.
		// This fails the call instead of doing a silent balance transfer.
		Err(<CrateError<T>>::UnsupportedPrecompileAddress.into())
	}
```

**File:** substrate/bin/node/runtime/src/lib.rs (L1608-1642)
```rust
impl pallet_revive::Config for Runtime {
	type Time = Timestamp;
	type Balance = Balance;
	type Currency = Balances;
	type RuntimeEvent = RuntimeEvent;
	type RuntimeCall = RuntimeCall;
	type RuntimeOrigin = RuntimeOrigin;
	type DepositPerItem = DepositPerItem;
	type DepositPerChildTrieItem = DepositPerChildTrieItem;
	type DepositPerByte = DepositPerByte;
	type WeightInfo = pallet_revive::weights::SubstrateWeight<Self>;
	type Precompiles = (
		ERC20<Self, InlineIdConfig<0x1>, Instance1>,
		ERC20<Self, InlineIdConfig<0x2>, Instance2>,
		VestingPrecompile<Self>,
	);
	type AddressMapper = pallet_revive::AccountId32Mapper<Self>;
	type RuntimeMemory = ConstU32<{ 128 * 1024 * 1024 }>;
	type PVFMemory = ConstU32<{ 512 * 1024 * 1024 }>;
	type UploadOrigin = EnsureSigned<Self::AccountId>;
	type InstantiateOrigin = EnsureSigned<Self::AccountId>;
	type RuntimeHoldReason = RuntimeHoldReason;
	type CodeHashLockupDepositPercent = CodeHashLockupDepositPercent;
	type ChainId = ConstU64<420_420_420>;
	type NativeToEthRatio = ConstU32<1_000_000>; // 10^(18 - 12) Eth is 10^18, Native is 10^12.
	type FindAuthor = <Runtime as pallet_authorship::Config>::FindAuthor;
	type AllowEVMBytecode = ConstBool<true>;
	type FeeInfo = pallet_revive::evm::fees::Info<Address, Signature, EthExtraImpl>;
	type MaxEthExtrinsicWeight = MaxEthExtrinsicWeight;
	type DebugEnabled = ConstBool<false>;
	type AutoMap = ConstBool<false>;
	type GasScale = ConstU32<1000>;
	type OnBurn = ();
	type Deposit = ();
}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs (L1372-1420)
```rust
impl pallet_revive::Config for Runtime {
	type Time = Timestamp;
	type Balance = Balance;
	type Currency = Balances;
	type RuntimeEvent = RuntimeEvent;
	type RuntimeCall = RuntimeCall;
	type RuntimeOrigin = RuntimeOrigin;
	type DepositPerItem = DepositPerItem;
	type DepositPerChildTrieItem = DepositPerChildTrieItem;
	type DepositPerByte = DepositPerByte;
	type WeightInfo = weights::pallet_revive::WeightInfo<Self>;
	type Precompiles = (
		ERC20<Self, InlineIdConfig<{ TRUST_BACKED_ASSETS_PRECOMPILE }>, TrustBackedAssetsInstance>,
		ERC20<Self, InlineIdConfig<{ POOL_ASSETS_PRECOMPILE }>, PoolAssetsInstance>,
		ERC20<
			Self,
			ForeignIdConfig<{ FOREIGN_ASSETS_PRECOMPILE }, Self, ForeignAssetsInstance>,
			ForeignAssetsInstance,
		>,
		XcmPrecompile<Self>,
		pallet_asset_conversion_precompiles::AssetConversion<{ ASSET_CONVERSION_PRECOMPILE }, Self>,
		VestingPrecompile<Self>,
	);
	type AddressMapper = pallet_revive::AccountId32Mapper<Self>;
	type RuntimeMemory = ConstU32<{ 128 * 1024 * 1024 }>;
	type PVFMemory = ConstU32<{ 512 * 1024 * 1024 }>;
	type AllowEVMBytecode = ConstBool<true>;
	type UploadOrigin = EnsureSigned<Self::AccountId>;
	type InstantiateOrigin = EnsureSigned<Self::AccountId>;
	type RuntimeHoldReason = RuntimeHoldReason;
	type CodeHashLockupDepositPercent = CodeHashLockupDepositPercent;
	type ChainId = ConstU64<420_420_421>;
	type NativeToEthRatio = ConstU32<1_000_000>; // 10^(18 - 12) Eth is 10^18, Native is 10^12.
	type FindAuthor = <Runtime as pallet_authorship::Config>::FindAuthor;
	type FeeInfo = pallet_revive::evm::fees::Info<Address, Signature, EthExtraImpl>;
	type MaxEthExtrinsicWeight = MaxEthExtrinsicWeight;
	type DebugEnabled = ConstBool<{ cfg!(revive_debug) }>;
	type AutoMap = ConstBool<true>;
	type GasScale = ConstU32<1000>;
	type OnBurn = Dap;
	type Deposit = pallet_revive::PGasDeposit<
		Runtime,
		Assets,
		AssetsHolder,
		AssetsFreezer,
		PGASAssetId,
		PGasRefundPercent,
	>;
}
```

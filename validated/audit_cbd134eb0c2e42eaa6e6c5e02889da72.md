## Non-18-Decimal Underlying Tokens Break `HyperFungibleToken` / `WrappedHyperFungibleToken` Cross-Chain Amount Accounting - ([File: sdk/packages/core/contracts/apps/HyperFungibleToken.sol], [File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken` can lock **any** ERC20 as `underlying` (its `configure()` sets `_underlying` to an arbitrary address with no decimals check), while the peer `HyperFungibleToken` deployed on remote chains always exposes the OpenZeppelin default `decimals() == 18` (never overridden). The cross-chain `Message.amount` field is passed through raw, with zero decimal scaling on-chain in either `send()` or `onAccept()`. If the wrapped underlying token is not 18-decimal (e.g. USDC with 6 decimals, WBTC with 8), the raw amount locked on the home chain and the raw amount minted on the remote chain represent wildly different real-world values, permanently mis-valuing/freezing bridged funds.

### Finding Description
`WrappedHyperFungibleToken.configure()` accepts an arbitrary `underlying` address with no decimals validation or storage of its decimals: [1](#0-0) 

`send()` locks `params.amount` raw units of `_underlying` and forwards the exact same raw `amount` in the cross-chain `Message`, with no decimal normalization: [2](#0-1) [3](#0-2) 

On the remote chain, `HyperFungibleToken` mints `message.amount` directly, and its `decimals()` is the inherited OpenZeppelin ERC20 default of 18 — it is never overridden or configured per-underlying-token: [4](#0-3) [5](#0-4) 

Nowhere in `HyperFungibleToken.sol` or `WrappedHyperFungibleToken.sol` is there any per-chain or per-token `decimals` field, unlike the equivalent Polkadot `pallet-hyper-fungible-token`, which explicitly stores `ChainConfig.decimals` per destination and calls `convert_to_erc20`/`convert_to_balance` to rescale amounts before dispatch: [6](#0-5) [7](#0-6) 

The `BridgeToken.sol` contract explicitly documents and handles exactly this class of issue for its own 12-decimal/18-decimal mismatch by having the pallet scale by `10^6`: [8](#0-7) 

This shows the protocol is aware decimals mismatches must be actively reconciled — but for the general-purpose `WrappedHyperFungibleToken` ↔ `HyperFungibleToken` pair (used for arbitrary ERC20s per the docs' USDC bridging examples), no such on-chain reconciliation exists. The developer docs even concede that decimal scaling is only handled off-chain, in the SDK, not enforced by the contracts themselves: [9](#0-8) 

This is the direct on-chain analog of the reported Angle Protocol issue: the specification/design implicitly assumes uniform decimals (here, "raw amount units are directly portable across HFT deployments"), but the code allows wrapping non-18-decimal tokens without any conversion, silently breaking value parity.

### Impact Explanation
If a deployer wraps a 6-decimal token (e.g. USDC) via `WrappedHyperFungibleToken` and pairs it with a standard `HyperFungibleToken` remote deployment (18 decimals, unmodifiable), then locking `1,000,000` raw units (1.0 USDC) mints `1,000,000` raw units on the remote chain — but because the remote token has 18 decimals, that mint amount is worth `0.000000000000000001` HFT, i.e., value is destroyed by a factor of 10^12. Conversely, burning a reasonable HFT balance to redeem USDC would require burning an amount so large it is practically unobtainable, permanently freezing the locked USDC in the wrapper contract (unreachable by users through the intended bridge flow). This is a permanent freezing/misaccounting of bridged value reachable by any ordinary user simply calling `send()` on a misconfigured (non-18-decimal) deployment — which the contracts do nothing to prevent or detect.

### Likelihood Explanation
Deployment of `WrappedHyperFungibleToken` for a non-18-decimal token is an explicitly supported, documented use case (the docs use "Wrapped USDC" as the canonical example, and USDC is 6-decimal), and there is no on-chain guard rejecting such underlying tokens. Any owner deploying a wrapper for USDC/USDT/WBTC/etc. without independently building an off-chain decimal-conversion layer (the docs say this is handled only by the SDK, not the contract) creates this exposure the moment users call `send()`.

### Recommendation
Add an on-chain decimals field (analogous to `pallet-hyper-fungible-token`'s `ChainConfig.decimals`) to both `HyperFungibleToken` and `WrappedHyperFungibleToken`, record the underlying/local decimals at `configure()`/`addChain()` time per peer chain, and rescale `message.amount` in `_buildDispatchPost` and `onAccept`/`onPostRequestTimeout` exactly as `convert_to_erc20`/`convert_to_balance` do for the substrate pallet, rather than relying on off-chain SDK scaling.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` on chain A with `_underlying` = USDC (6 decimals) via `configure()` [1](#0-0) .
2. Deploy `HyperFungibleToken` on chain B (18 decimals, default) and register both as peers via `addChain()`.
3. User calls `send()` on chain A with `params.amount = 1_000_000` (1.0 USDC): USDC is locked, and `Message.amount = 1_000_000` is dispatched [3](#0-2) .
4. On chain B, `onAccept` mints `message.amount = 1_000_000` wei of the 18-decimal HFT token to the recipient [10](#0-9) , i.e., 0.000000000000000001 HFT — a 10^12 devaluation of the bridged 1 USDC, with the underlying USDC now unrecoverable at parity through the bridge's normal `send()`/burn flow.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L178-185)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-253)
```text
    function _buildDispatchPost(HyperFungibleToken.SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(HyperFungibleToken.Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L44-44)
```text
contract HyperFungibleToken is ERC20, ERC165, HyperApp, Ownable, Pausable {
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

**File:** modules/pallets/hyper-fungible-token/src/impls.rs (L43-59)
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

/// Converts a local u128 balance to an ERC20 U256 amount
///
/// Multiplies by 10^(erc_decimals - local_decimals) to scale up to ERC20 precision
pub fn convert_to_erc20(value: u128, erc_decimals: u8, local_decimals: u8) -> U256 {
	U256::from(value) * U256::from(10u128.pow(erc_decimals.saturating_sub(local_decimals) as u32))
}
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-302)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};
```

**File:** evm/src/apps/BridgeToken.sol (L34-36)
```text
 * `decimals()` is the inherited ERC20 default of 18 while BRIDGE is 12 decimals on nexus, so the
 * pallet scales by 10^6 in both directions. The chain config registered on nexus via `register_token`
 * must therefore declare 18 decimals for this contract.
```

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L111-111)
```text
For a higher-level experience, the [TypeScript SDK](/developers/sdk/hyper-fungible-token) handles fee estimation, token approvals, and decimal scaling automatically.
```

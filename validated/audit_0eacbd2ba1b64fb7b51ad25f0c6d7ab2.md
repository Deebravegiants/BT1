### Title
Fee-on-transfer or deflationary underlying tokens cause unbacked mint/unlock in `WrappedHyperFungibleToken`, leading to escrow insolvency — (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
The reported bug class is a token whose backing collateral can silently shrink relative to what was recorded, with no reconciliation/burn mechanism, leading to depeg and insolvency. The reachable analog in Hyperbridge is `WrappedHyperFungibleToken.send()`, which locks an underlying ERC20 via `safeTransferFrom` but always dispatches the caller-supplied `params.amount` as the cross-chain mint/unlock instruction, regardless of how much the contract actually received or continues to hold. A fee-on-transfer or deflationary/rebasing underlying token causes the escrowed balance to be permanently less than the sum of amounts promised to remote chains.

### Finding Description
`send()` transfers tokens into the contract without measuring the actual amount received: [1](#0-0) 

Specifically, for non-WETH underlyings it calls `IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount)` and then immediately builds the dispatch body with the unmodified `params.amount`: [2](#0-1) 

On the destination chain, `HyperFungibleToken.onAccept` mints (or the wrapper unlocks) exactly `message.amount` — the same, unadjusted figure — to the beneficiary: [3](#0-2) 

If `_underlying` is a fee-on-transfer token, the contract receives `amount - fee` but promises `amount` cross-chain. If it is a rebasing/deflationary token, the escrow's balance can later drop below the sum of amounts it has promised, even for tokens that transferred cleanly at lock time. Either way, the invariant "1 unlocked/minted representative token is backed by 1 escrowed underlying token" (documented explicitly for the analogous `BridgeToken`/nexus-escrow model) is violated: [4](#0-3) 

Notably, the codebase is aware of exactly this risk class and defends against it elsewhere — `IntentGatewayV2` computes the actual `receivedByGateway` amount after a fee-on-transfer deduction and uses that reduced figure for escrow accounting: [5](#0-4) 

`WrappedHyperFungibleToken` has no equivalent balance-before/after check, so it lacks the same protection.

### Impact Explanation
Each lock operation with a deflating/fee-charging/rebasing underlying widens the gap between (a) the sum of amounts promised as mints/unlocks on all peer chains and (b) the actual token balance held by the escrow contract. Because there is no burn-on-shortfall or rebalancing mechanism (mirroring the missing "burn dETH on slashing" mitigation in the original report), the deficit is permanent and compounds with volume. Eventually a legitimate unlock/refund (`onAccept` or `onPostRequestTimeout`, both of which call `safeTransfer`) will revert due to insufficient underlying balance, freezing funds for whichever user's withdrawal exhausts the shortfall — a concrete case of permanent freezing of funds / unbacked cross-chain claims.

### Likelihood Explanation
This requires only a single unprivileged transaction: any user calling `send()` on a `WrappedHyperFungibleToken` deployment configured with (or later migrated/compatible with) a fee-on-transfer or deflationary ERC20 as `_underlying`. No attacker privilege, governance, or admin action is needed — the owner merely needs to have wrapped a non-standard ERC20, which is common in production token ecosystems (many popular tokens include transfer fees or rebasing). The codebase's own explicit handling of this exact pattern in `IntentGatewayV2` shows the risk is already recognized as realistic, but the fix was not applied to `WrappedHyperFungibleToken`.

### Recommendation
In `WrappedHyperFungibleToken.send()`, measure the contract's underlying token balance before and after `safeTransferFrom` and use the actual received delta (not the caller-supplied `params.amount`) when building the dispatched `Message.amount`. Alternatively, explicitly document and enforce (e.g., via an allowlist or ERC20 metadata check) that only standard, non-fee, non-rebasing tokens may be configured as `_underlying`, and reject deployments/configuration for tokens found not to conform.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` with `_underlying` set to a fee-on-transfer ERC20 (e.g., 1% fee on transfer, similar to the `FeeOnTransferToken` used in `IntentGatewayV2SameChainTest.sol`).
2. User calls `send({dest, to, amount: 1000e18, ...})`. `safeTransferFrom` moves `1000e18` from the user, but only `990e18` lands in the contract (1% fee burned/redirected).
3. `_buildDispatchPost` still encodes `amount: 1000e18` in `Message`, and the ISMP request is dispatched with that full amount.
4. On the destination chain, `onAccept` mints/unlocks `1000e18` to the beneficiary — 10e18 more than what is actually escrowed on the source chain.
5. Repeating this drains the escrow's backing ratio below 100%. When enough remote holders attempt to bridge back and call `onAccept`/`onPostRequestTimeout` (both doing `safeTransfer` of the full promised amount) on the source chain, a later transfer reverts once the escrow's real balance is exhausted, freezing that user's funds.

### Citations

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

**File:** evm/src/apps/BridgeToken.sol (L26-29)
```text
 * @dev BRIDGE is native to nexus, so the two ends run the escrow model: `pallet-hyper-fungible-token`
 * escrows the native balance on nexus and this contract mints the equivalent here, meaning the supply
 * of this token is always backed by the pallet's escrow account. Sending back burns here and releases
 * there.
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2558-2568)
```text
    /// @notice Full round-trip: place with fee-on-transfer, fill, solver withdraws exact escrow.
    function testPlaceAndFill_FeeOnTransferToken_RoundTrip() public {
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 receivedByGateway = inputAmount - (inputAmount * 100) / 10000; // 990
        uint256 outputAmount = 900 * 1e18;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});
```

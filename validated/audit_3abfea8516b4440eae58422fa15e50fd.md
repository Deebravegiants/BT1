### Title
Solver's cross-chain escrow redemption is hardcoded to `msg.sender`, causing permanent loss for solvers using Account Abstraction wallets or multisigs - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`ExtrinsicIntents._fillCrossChain` hardcodes the beneficiary of the `RedeemEscrow` message that unlocks the user's escrowed input tokens on the **source** chain to `msg.sender` on the **destination** chain, with no parameter allowing the solver to specify a different recipient address for the source chain. This is the same address-symmetry bug class as the reported `UnstakeMessenger.unstake` finding: it assumes the solver controls the identical address on both chains.

### Finding Description
When a solver fills a cross-chain order, `_fillCrossChain` builds the redemption body directly from `msg.sender`: [1](#0-0) 

Specifically, the beneficiary field of the `RedeemEscrow` withdrawal request dispatched back to the source chain is set to `bytes32(uint256(uint160(msg.sender)))` — the solver's address as observed on the **destination** chain:
```
_post(
    order,
    _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
    options.relayerFee,
    nativeFee
);
```
This message is delivered via `onAccept` on the source chain's `IntentGateway`, which calls `withdraw()` to transfer the escrowed input tokens directly to that same raw address on the **source** chain (per the documented flow: "Transfers each escrowed input token to the solver").

There is no field in `FillOptions` (the solver-supplied fill parameters) that lets the solver designate an alternate source-chain recipient — the beneficiary is derived exclusively from `msg.sender` at fill time on the destination chain.

This mirrors the reported `UnstakeMessenger.unstake` bug exactly: a message constructed on one chain hardcodes a recipient field to the local caller's address, and that field is later used as the destination for a fund transfer on a *different* chain, assuming the caller's address is identical across chains.

### Impact Explanation
Solvers/fillers frequently operate through smart-contract wallets (Gnosis Safe multisigs, AA wallets, relayer-operated proxy contracts) for security or operational reasons. Because contract addresses are deployment-dependent (different nonce, different `CREATE2` salt/factory state, or simply not deployed at all on a given chain), the solver's address on the destination chain can differ from — or simply not exist as a controlled account on — the source chain. When `_fillCrossChain` hardcodes the beneficiary to the destination-chain `msg.sender`, the escrowed input tokens released on the source chain (potentially large USDC/stablecoin/DAI amounts, as seen in `IntentGatewayV2Test.sol`) are sent to an address the solver may not control on that chain. This results in a permanent, unrecoverable loss of the escrowed input tokens for any solver whose address differs across the two chains — a direct loss-of-funds impact analogous to the referenced report's "permanent loss of assets" conclusion.

### Likelihood Explanation
This path is reachable by any unprivileged solver simply calling the standard `fillOrder`/`_fillCrossChain` function — no special privileges, governance, or malicious actors are required. Smart contract wallets and multisigs are an increasingly common way to operate solver/filler infrastructure (for key-management and operational-security reasons), so encountering an address mismatch across chains is a realistic and not a merely theoretical occurrence, matching the same protocol-level assumption flaw as the analogous finding.

### Recommendation
Add an optional `recipient`/`beneficiary` field to `FillOptions` (or a dedicated parameter to `fillOrder`) that lets the solver explicitly specify the source-chain address that should receive the redeemed escrow, defaulting to `msg.sender` only when unset:
```solidity
bytes32 targetBeneficiary = options.recipient == bytes32(0)
    ? bytes32(uint256(uint160(msg.sender)))
    : options.recipient;

_post(
    order,
    _body(RequestKind.RedeemEscrow, commitment, order.inputs, targetBeneficiary),
    options.relayerFee,
    nativeFee
);
```
This removes the implicit assumption of address symmetry across chains and lets solvers using AA wallets/multisigs safely designate the correct source-chain recipient.

### Proof of Concept
1. A solver operates via a Gnosis Safe deployed at address `0xAAAA...` on the destination chain (e.g., via `CREATE2` with nonce N).
2. On the source chain, the solver's Safe (same owners) is deployed with a different nonce, resulting in address `0xBBBB...` — a completely different address, or the Safe may not be deployed there at all.
3. The solver calls `fillOrder`/`_fillCrossChain` from `0xAAAA...` on the destination chain, providing output tokens to the order's beneficiary.
4. `_fillCrossChain` dispatches `RedeemEscrow` with `beneficiary = bytes32(uint256(uint160(0xAAAA...)))`.
5. On the source chain, `onAccept` → `withdraw()` transfers the escrowed input tokens to raw address `0xAAAA...`, which the solver's multisig does not control on the source chain (or which may be an uninitialized/undeployed contract address).
6. The escrowed tokens are permanently locked/lost to the solver, since they were never able to specify their true source-chain-controlled address as the beneficiary. [2](#0-1)

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-220)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
    }
```

### Title
Cross-chain fill escrow releases funds to `msg.sender`'s destination-chain address, not a user-chosen address on the source chain - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`_fillCrossChain` in the Intent Gateway's cross-chain fill path encodes `msg.sender` (the solver's address as it exists on the **destination** chain) as the escrow beneficiary for the `RedeemEscrow` message sent back to the **source** chain, without allowing the solver to specify a different receiving address on the source chain.

### Finding Description
When a solver fills a cross-chain order, `_fillCrossChain` builds the settlement message that will unlock the escrowed input tokens on the source chain: [1](#0-0) 

```solidity
_post(
    order,
    _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
    options.relayerFee,
    nativeFee
);
```

`msg.sender` here is the solver's address as observed on the destination chain (where `fillOrder`/`_fillCrossChain` executes). This value is hard-coded as the `beneficiary` in the `WithdrawalRequest` that is dispatched to the source chain. When the message arrives on the source chain, `onAccept` decodes the beneficiary and transfers the escrowed input tokens directly to that address: [2](#0-1) 

There is no field in `FillOptions`/`Order` that lets the solver supply an explicit, chain-specific redemption address for the source chain. This mirrors the reported bug class: the protocol assumes a single logical actor's address is identical across two different chains. For account-abstraction wallets (Safe, ERC-4337 smart accounts, proxies deployed via CREATE2 with chain-specific factories/nonces, EIP-7702 accounts, etc.), the solver's contract address on the destination chain can differ from — or simply not exist as a controllable address on — the source chain. The Intent Gateway's own docs describe solver infrastructure built around smart contract wallets (`SolverAccount`, ERC-4337, EIP-7702), making this a realistic scenario rather than a theoretical edge case: [3](#0-2) 

### Impact Explanation
If a solver's fill transaction is submitted from a smart-contract address (a `SolverAccount`, multisig, or any AA wallet) whose address differs between the destination and source chains, the escrowed input tokens released via `RedeemEscrow` are sent to `msg.sender`'s address value reinterpreted on the source chain — an address the solver may not control there. This results in permanent loss of the escrowed input tokens (concrete theft/permanent freezing of funds), since there is no mechanism to redirect or recover funds sent to an uncontrolled address once `_filled[commitment]` is set and the source-chain transfer executes.

### Likelihood Explanation
Likelihood is elevated because the protocol explicitly supports and documents smart-contract-wallet-based solvers (`SolverAccount` combining ERC-4337 + EIP-7702 + ERC-7821), which are exactly the account types prone to divergent addresses across chains due to different factory deployments, nonces, or delegation state per chain. Any solver using such an account for cross-chain fills is exposed on every fill, requiring no attacker — just normal use of AA-based solver infrastructure with mismatched deployment addresses.

### Recommendation
Add an explicit `redeemBeneficiary` (or similar) field to `FillOptions` that the solver supplies at fill time, and use that value instead of `msg.sender` when constructing the `RedeemEscrow` body:

```solidity
function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
    ...
    require(options.redeemBeneficiary != bytes32(0), "Invalid beneficiary");
    _post(
        order,
        _body(RequestKind.RedeemEscrow, commitment, order.inputs, options.redeemBeneficiary),
        options.relayerFee,
        nativeFee
    );
    ...
}
```
This lets solvers designate the correct address on the source chain to receive the redeemed escrow, independent of their destination-chain execution address.

### Proof of Concept
1. Solver deploys/operates a `SolverAccount` (ERC-4337/EIP-7702 smart account) at address `0xSolverDest` on the destination chain (e.g., Arbitrum).
2. The same logical solver's smart account on the source chain (e.g., Ethereum) has a different address `0xSolverSource` (different factory salt/nonce/deployment state).
3. Solver calls `fillOrder` → `_fillCrossChain` on Arbitrum as `0xSolverDest`, delivering output tokens to the order's beneficiary.
4. `_fillCrossChain` encodes `bytes32(uint256(uint160(msg.sender)))` = `0xSolverDest` as the `RedeemEscrow` beneficiary and dispatches it to Ethereum.
5. On Ethereum, `onAccept`/`withdraw` transfers the escrowed input tokens (e.g., USDC) to `0xSolverDest`.
6. If `0xSolverDest` has no corresponding deployed contract/logic on Ethereum (or a different owner controls it there), the solver's escrowed tokens are locked or lost.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L201-220)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L481-485)
```text
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
    }
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L118-123)
```text
### `SolverAccount`

The SolverAccount is a smart account designed for solvers that combines [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) (account abstraction), [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702), and [ERC-7821](https://eips.ethereum.org/EIPS/eip-7821) (batch execution) to batch `gateway.select(...)` and `gateway.fillOrder(...)` into a single atomic UserOperation. Solvers delegate their EOA to the SolverAccount via EIP-7702 and submit bundled operations through the ERC-4337 EntryPoint.

`SolverAccount.validateUserOp` accepts two signature formats, discriminated by length: a standard 65-byte ECDSA signature over the `userOpHash` for regular account operations (delegation no-ops, approvals, treasury batches), and the 162-byte intent-selection payload `abi.encodePacked(commitment, solverSignature, sessionSignature)` for fills. UserOperations whose calldata contains a `fillOrder` call to the gateway are refused on the standard path. This guard exists because bids are public on Hyperbridge and embed a valid 65-byte solver signature over the `userOpHash` — without it, anyone could strip the commitment and session signature from a bid and submit the bare operation: the fill would revert (no selection is staged during validation), but it would still consume the bid's nonce and gr ... (truncated)

```

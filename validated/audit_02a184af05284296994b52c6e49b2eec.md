### Title
Swap external action accepts any output amount because the signed slippage floor is checked for non‑zero but never enforced against the router result - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap.swap()` requires that `circomData.slippageValues[1]` is non‑zero, but never compares the actual `swappedAmount` returned by the DEX router to that floor. The floor value is signed by the user (it is hashed into `calldataHash`/`signedMessageHash`) but is dead data on-chain, so the shielded output UTXO can be created for far less value than the user authorized.

### Finding Description
In the swap flow, the user's ZK-signed request encodes a minimum acceptable output via `circomData.slippageValues[1]`, which is committed inside `getHashedCalldata1` and therefore inside the `calldataHash`/`signedMessageHash` that the EdDSA signature covers [1](#0-0) . However `ExternalActionSwap.swap()` only checks that the value is set, not that it is respected:

```
require(
    circomData.slippageValues[1] != 0,
    "swap output slippage floor not set"
);
...
uint256 swappedAmount = callRouter(...);
``` [2](#0-1) 

After the router call, `swappedAmount` is used unconditionally to compute fees and the amount forwarded into the newly minted shielded UTXO, with no comparison to `slippageValues[1]`: [3](#0-2) 

This is structurally the same class of bug as the referenced Frax report: a value the user explicitly signed for as a protection bound (`maxAmount`/slippage floor) is not actually used to gate the state-dependent, volatile result of an external call (`previewMint()` / router swap output). Here the outcome is worse than in the Frax report — instead of the transaction simply reverting on a mismatch, the transaction *succeeds* with an output far below what was signed, and the shielded UTXO is minted for the reduced (attacker/MEV-favorable) amount. Since `amountChanges` (and thus the ZK circuit's `inTotal + amountChanges === outTotal` equality) is driven by the *actual* post-swap value rather than by the user-approved floor, the on-chain equality holds even though the user's intended value-preservation guarantee is broken.

### Impact Explanation
A user (or their relay acting on their behalf) submitting a shielded swap has no on-chain protection against adverse execution (e.g., sandwich attacks, stale quotes, or a router returning a degraded amount), despite believing they had signed for a floor. The shielded balance minted into the tree can be silently reduced relative to what the user authorized, resulting in direct loss of in-flight shielded value during the swap. This meets the Critical bar ("direct theft of shielded or in-flight user funds") because the deficiency is enforced nowhere else in the call path — `slippageValues[1]` is otherwise inert.

### Likelihood Explanation
Any user calling the swap external action is affected; no privileged role, admin key, or malicious relayer collusion is required — ordinary public-mempool MEV/sandwiching against the router call is sufficient to trigger loss, since the intended floor check is simply absent from the code path that would have prevented it.

### Recommendation
Enforce the signed slippage floor against the actual result:
```solidity
require(
    swappedAmount >= uint256(circomData.slippageValues[1]),
    "swap output below signed slippage floor"
);
```
placed immediately after `callRouter(...)` returns, before fees/UTXO creation are computed.

### Proof of Concept
1. User submits a shielded swap with `circomData.slippageValues[1] = 1000` (their signed minimum acceptable output) and `circomData.amountChanges` etc. hashed into `calldataHash`/`signedMessageHash`.
2. The transaction is included in a block where an unrelated actor sandwiches the router call (or the router itself yields a degraded quote), causing `callRouter(...)` in [4](#0-3)  to return `swappedAmount = 1` instead of the expected ~1000.
3. Because the only check performed is `slippageValues[1] != 0` (line 54), execution proceeds; fees are deducted from `swappedAmount`, and a UTXO of `amountToSendToHinkal` (effectively dust) is created and inserted into the shielded pool for the user [5](#0-4) .
4. The user's signed floor of 1000 was never actually enforced, and they receive a shielded balance far below their signed expectation, with the difference captured elsewhere (e.g., by the sandwiching party).

### Citations

**File:** contracts/CircomDataBuilder.sol (L20-35)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L53-68)
```text
        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-101)
```text
        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
        }

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);

        utxoSet = new UTXO[](1);
        utxoSet[0] = UTXO({
            amount: amountToSendToHinkal,
            erc20Address: outputToken,
            stealthAddressStructure: circomData.stealthAddressStructure,
            timeStamp: block.timestamp
        });
```

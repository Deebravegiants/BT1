Found a direct analog in `DepositOnChainUtxosExternalAction.sol`. This mirrors the Connext bug class: a token movement is authorized using a party's balance/allowance that isn't the actual counted, calldata-hash-bound authorizer of that specific value.

### Title
`DepositOnChainUtxosExternalAction.runAction` pulls funds via `transferFrom(userAddress, ...)` where `userAddress` (`circomData.originalSender`) is not cryptographically bound to the UTXO amounts being created - (File: `contracts/external-actions/DepositOnChainUtxosExternalAction.sol`)

### Summary
`runAction()` reads `userAddress = circomData.originalSender` and uses it as the `_from` in `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` [1](#0-0) , pulling `tokenTotal` (derived from `utxoAmounts`, decoded from `externalActionData.externalActionMetadata`) directly from that address's allowance to this contract [2](#0-1) .

### Finding Description
The Connext report's root cause was that a value-moving operation (`swapInternal`) checked/consumed a balance belonging to `msg.sender` (the relayer) instead of the actual party who should fund the operation, breaking the intended equality between "who is charged" and "who authorized the charge." Here, `runAction` is called by `Hinkal.sol` itself (`msg.sender` inside this contract equals the Hinkal diamond/proxy per the `onlyAllowedRecipient` modifier) [3](#0-2) , but the actual token debit is performed against `circomData.originalSender`, an address supplied as ordinary calldata rather than an address whose spending was authorized by an EdDSA-signed proof over the UTXO amounts.

`circomData.originalSender` is checked elsewhere only against `msg.sender` of the top-level `execute`/`transact` call when `relay == address(0)` (`performHinkalChecks` in `HinkalHelper.sol`) — i.e., it enforces that `originalSender == the direct caller`, not that `originalSender` has consented via the ZK proof to have exactly `tokenTotal` pulled from their wallet for these specific UTXO amounts. The UTXO amounts (`utxoAmounts`) come from `externalActionData.externalActionMetadata`, which is hashed into `calldataHash` [4](#0-3)  and thus into the EdDSA-signed message — but that signature is produced by the *spendingPublicKey* of the note owner receiving the new UTXOs, not necessarily by `originalSender`. There is no on-chain check that `originalSender` approved this specific `tokenTotal`/`utxoAmounts` combination beyond a pre-existing ERC20 `approve()` to the contract. Any caller who routes a transaction through the allowed relay/Hinkal path with an `originalSender` address that has outstanding ERC20 allowance to this contract (a common pattern for users who have previously interacted with `DepositOnChainUtxosExternalAction` or any contract sharing this allowance) can specify arbitrary `utxoAmounts` in metadata and drain that allowance to mint themselves shielded UTXOs, since `deltaAmounts[i] == 0` is required (bypassing the normal `Hinkal.sol` balance-equality/slippage check that would otherwise force the caller's own balance to decrease by the withdrawn amount) [5](#0-4) .

Because `deltaAmounts[i]` must be `0`, `Hinkal.sol`'s post-call balance-diff/slippage check (`balanceDif >= circomData.slippageValues[i]`) [6](#0-5)  does not constrain this transfer at all with respect to `originalSender`'s balance — the `deltaAmountChanges` used in `_externalTransact` only governs transfers between `Hinkal.sol` and the external action address, not the `transferFrom(userAddress, ...)` performed independently inside `runAction`. This decouples the value pulled from `originalSender` from any amount actually reflected in Hinkal's balance-equation checks or circuit-verified `amountChanges`.

### Impact Explanation
This breaks the equality that "value entering the shielded pool must equal value debited from an authorizing party, as attested by the ZK proof/public inputs." If `originalSender` has any live ERC20 allowance toward this external action contract, an attacker (the actual `msg.sender`/relay-selectable caller of `Hinkal.execute`) can set `circomData.originalSender` to that victim's address and mint themselves arbitrary shielded UTXOs funded by the victim's tokens up to the allowance, with the victim's EdDSA/spending key never having signed off on these specific UTXO amounts. This is theft of user funds (Critical) if such an allowance exists (e.g., left over from a prior legitimate deposit that didn't fully consume the approval, or infinite-approval patterns common in this codebase's `approveUnlimited`/`_pullAndApproveDepositTokens` flows).

### Likelihood Explanation
Requires the victim to have a non-zero standing ERC20 allowance to this specific external-action contract. Given the codebase's own pattern of `approveUnlimited` for router contracts and unique-token approval flows in `HinkalWrapper._pullAndApproveDepositTokens` [7](#0-6) , users interacting with wrapper/router-style flows plausibly leave residual allowances to adjacent contracts; if any user ever grants allowance directly to `DepositOnChainUtxosExternalAction`, exploitation requires only calling `Hinkal.execute` with a proof for the attacker's own valid nullifiers/circuit constraints but an arbitrary `originalSender` in calldata and `externalActionId` pointing to this action.

### Recommendation
Do not use a calldata-supplied `originalSender`/arbitrary address as the source of `transferFrom` in `DepositOnChainUtxosExternalAction`. The debited party must be cryptographically bound to the exact `utxoAmounts`/`tokenTotal` being created — e.g., require `originalSender == msg.sender` of the top-level `Hinkal` call (not just when `relay == address(0)`), or better, require the deposit source to be `msg.sender` of `execute()` itself (mirroring `_internalTransact`'s check `externalActionData.externalAddress == msg.sender` for deposits) [8](#0-7) , and fold `utxoAmounts`/`tokenTotal` into the balance-equation check enforced by `Hinkal.sol` rather than trusting the external action's internal `transferFrom`.

### Proof of Concept
1. Victim V previously approved contract `D` (`DepositOnChainUtxosExternalAction`) for token T with a large/unlimited allowance (e.g., via a legitimate deposit flow that left dust allowance, or an infinite-approve UX pattern).
2. Attacker A constructs a valid ZK proof for their own existing UTXOs/nullifiers (satisfying all in-circuit constraints, unrelated to V), sets `circomData.originalSender = V`'s address, `externalActionData.externalActionId` = D's id, `externalActionData.externalActionMetadata = abi.encode(utxoAmounts)` specifying large amounts for token T, and `deltaAmounts[i] = 0` for T.
3. Attacker calls `Hinkal.execute` via the relay path (`relay != address(0)`, so the `originalSender == sender` check is skipped) or directly if `originalSender == msg.sender` is satisfiable by having A itself be V is not required since the check only fires when `relay == address(0)`.
4. `Hinkal._externalTransact` invokes `D.runAction`, which calls `transferERC20TokenFrom(T, V, D, tokenTotal)`, pulling V's tokens using V's stale allowance.
5. New shielded UTXOs of `utxoAmounts` are created for the attacker's stealth address, funded entirely by V's tokens, with no signature from V's spending key authorizing this specific withdrawal.

### Citations

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-35)
```text
        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-53)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L75-82)
```text
            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L16-22)
```text
    modifier onlyAllowedRecipient() {
        require(
            isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```

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

**File:** contracts/Hinkal.sol (L100-114)
```text
                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );
```

**File:** contracts/Hinkal.sol (L177-187)
```text
            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
```

**File:** contracts/HinkalWrapper.sol (L72-109)
```text
    function _pullAndApproveDepositTokens(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts
    ) internal {
        uint256 len = erc20Addresses.length;
        address[] memory uniqueTokens = new address[](len);
        uint256[] memory uniqueAmounts = new uint256[](len);
        uint256 uniqueCount;

        for (uint256 i = 0; i < len; i++) {
            address token = erc20Addresses[i];
            if (token == address(0) || amounts[i] == 0) continue;

            transferERC20TokenFrom(
                token,
                msg.sender,
                address(this),
                amounts[i]
            );

            uint256 idx = uniqueCount;
            for (uint256 j = 0; j < uniqueCount; j++) {
                if (uniqueTokens[j] == token) {
                    idx = j;
                    break;
                }
            }
            if (idx == uniqueCount) {
                uniqueTokens[uniqueCount] = token;
                uniqueCount++;
            }
            uniqueAmounts[idx] += amounts[i];
        }

        for (uint256 k = 0; k < uniqueCount; k++) {
            approveERC20Token(uniqueTokens[k], hinkal, uniqueAmounts[k]);
        }
    }
```

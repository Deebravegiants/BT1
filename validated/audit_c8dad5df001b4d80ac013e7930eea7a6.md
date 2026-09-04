### Title
Attacker drains any leftover ERC20 balance held by the Emporium contract via unrestricted stateless op calls - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction()` executes a user-supplied `EmporiumStack` of `EmporiumOperation`s against arbitrary endpoints/calldata, and only reconciles the Emporium contract's balance for the tokens the caller declares in `circomData.erc20TokenAddresses`. Any ERC20 balance sitting in the Emporium contract that is not part of that declared token list (leftover reward/dust tokens accrued from a prior interaction, unswept remainders, rounding leftovers, etc.) is never checked by Hinkal's balance-diff invariant, and can be moved out of the contract by *any* unprivileged caller through a "stateless" op that directly calls `token.transfer(attacker, amount)` from the Emporium's own context.

### Finding Description
In `EmporiumUpgradeable.runAction()` (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol:76-160), stateless operations execute arbitrary calls from the Emporium contract itself: [1](#0-0) 

The only restriction is a selector blacklist preventing an attacker from calling `IHinkalWallet.callHinkalWallet` / `doSendToRelay` directly: [2](#0-1) 

Nothing prevents `op.endpoint` from being an arbitrary ERC20 token and `op.callData` from being `transfer(attacker, amount)`. Since this call is made by the Emporium contract (`msg.sender == Emporium`), any token balance the Emporium holds — including reward/leftover tokens from a previous user's DeFi interaction through the same shared contract that were not included in that transaction's `erc20TokenAddresses` — can be siphoned out.

Crucially, the post-action reconciliation in `runAction()` only checks balance deltas for the tokens declared by the *current* caller: [3](#0-2) 

If the stolen token is simply omitted from `circomData.erc20TokenAddresses`, no invariant is ever checked against it — it is a balance moved by an external action but never counted in the balance equation, matching the report's root cause ("only refunds some tokens, the rest stay in the contract and can be stolen by whoever invokes the transfer with the same address token").

The attack is trivially reachable because `circomData.erc20TokenAddresses` can legally be empty for Emporium actions, which routes to a minimal circuit (`MainEVMCircuitMin`) requiring no real UTXO ownership at all: [4](#0-3) [5](#0-4) 

An attacker only needs `messageSeed` (freely chosen) and a matching `calldataHash` over their own crafted `CircomData` (including the malicious `EmporiumStack` in `externalActionMetadata`), which is easy to compute themselves — `calldataHash` binds the ops to the proof, but does not restrict *what* the attacker can put in the ops when it's their own transaction: [6](#0-5) 

With `signerAddress == address(0)` in the `EmporiumStack`, `verifyWallet()` skips all signature verification entirely: [7](#0-6) 

So the attacker submits `transact()` with `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, and a stack whose sole op is `leftoverToken.transfer(attacker, stuckBalance)` with `invokeWallet = false`. No UTXOs, nullifiers, or the target token need to appear anywhere in the checked equality.

### Impact Explanation
This allows an unprivileged attacker to steal any ERC20 balance parked in the Emporium contract that is not part of a given transaction's declared token set — e.g., dust/reward remainders left over from other users' external DeFi interactions routed through Emporium, or relay-fee remainders. This is direct theft of protocol/relay/user funds held by the contract with no authorization from the depositor or a wallet signer, matching High/Critical severity ("theft of protocol/relay fees", "unauthorised asset movement").

### Likelihood Explanation
High. No privileged role, relayer cooperation, or victim signature is required. The attacker only needs to observe that the Emporium contract holds a stray ERC20 balance (visible on-chain) and submit one `transact()` call with a trivially satisfiable minimal-circuit proof and a stateless transfer op.

### Recommendation
- Require `runAction`/Emporium stateless ops to only ever move tokens that are part of `circomData.erc20TokenAddresses`, or otherwise disallow arbitrary `endpoint.call` targets that are plain ERC20 tokens (e.g., block calls whose selector matches `transfer`/`transferFrom`/`approve` when invoked in stateless mode with `signerAddress == 0`).
- Do not allow zero-length `erc20TokenAddresses` for Emporium actions that execute stateless operations capable of moving arbitrary tokens; require every token the ops can touch to be declared and reconciled by the balance-diff invariant.
- Sweep/refund all non-zero token balances left in the Emporium contract at the end of every `runAction` call, not just the declared token list, so no value can persist unaccounted-for between transactions.

### Proof of Concept
1. Emporium contract accumulates a leftover ERC20 balance `R` of `RewardToken` (e.g., from a prior user's ops interacting with a yield/staking endpoint that returned extra reward tokens the user didn't declare/list).
2. Attacker (no funds, no proof-relevant UTXOs) builds `CircomData` with `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, and `externalActionMetadata` encoding an `EmporiumStack{ signerAddress: address(0), ops: [{ endpoint: RewardToken, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, R)) }] }`.
3. Attacker computes `calldataHash` per `CircomDataBuilder.getHashedCalldata` and generates a trivial `MainEVMCircuitMin` proof (`messageSeed` freely chosen).
4. Attacker calls `Hinkal.transact()`. `performHinkalChecks` passes (hash matches, dimensions match empty arrays), proof verifies, `_externalTransact` routes to `EmporiumUpgradeable.runAction`.
5. `runAction` executes the stateless op: `RewardToken.transfer(attacker, R)` is executed with `msg.sender == Emporium`, draining `R` to the attacker. No balance-diff check ever inspects `RewardToken` since it is absent from `erc20TokenAddresses`.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L102-113)
```text
            // CASE 2: Stateless Interaction
            else {
                bytes4 selector = bytes4(op.callData);
                if (
                    selector == IHinkalWallet.callHinkalWallet.selector ||
                    selector == IHinkalWallet.doSendToRelay.selector
                ) {
                    revert UnauthorizedWalletCall();
                }

                (success, err) = op.endpoint.call{value: op.value}(op.callData);
            }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-151)
```text
        uint256[] memory balancesAfter = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        UTXO[] memory utxoSet = new UTXO[](
            circomData.erc20TokenAddresses.length
        );

        uint256 utxoSetLength;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 balanceChange = int256(balancesAfter[i]) -
                int256(balancesBefore[i]);

            if (deltaAmountChanges[i] < 0) {
                balanceChange -= deltaAmountChanges[i];
                // this equation reads: total change of emporium balance = what was moved to emporium (-deltaAmountChange) + how emporium balance changed through tx (balanceChange)
            }

            // the only case when balanceChange can be < 0, when there were some funds on emporium before the call
            if (balanceChange < 0) {
                revert BalanceChangeShouldBePositive();
            }

            UTXO memory utxoOut = handleOut(balanceChange, circomData, i);

            if (utxoOut.amount > 0) {
                utxoSet[utxoSetLength++] = utxoOut;
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-316)
```text
    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/CircomDataBuilder.sol (L10-35)
```text
    function getHashedCalldata(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        // because of stack too deep error, we need to split the calldata into two parts
        uint256 calldataHash1 = getHashedCalldata1(circomData);
        uint256 calldataHash2 = getHashedCalldata2(circomData);
        return (uint256(keccak256(abi.encode(calldataHash1, calldataHash2))) %
            CIRCOM_P);
    }

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

**File:** contracts/CircomDataBuilder.sol (L139-161)
```text
        if (
            circomData.externalActionData.externalActionId ==
            HINKAL_EMPORIUM_ACTION_ID &&
            circomData.erc20TokenAddresses.length == 0
        ) {
            return formInputEmporiumMin(circomData);
        } else {
            return formInputNormal(chainId, verifyingContract, circomData);
        }
    }

    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }
```

**File:** circuits/MainEVMCircuitMin.circom (L1-18)
```text

pragma circom 2.1.6;

include "../../node_modules/circomlib/circuits/poseidon.circom";

template MainEVMCircuitMin() {
  // Public inputs:
  signal input outTimeStamp;
  signal input calldataHash;

  // Private inputs:
  signal input messageSeed;

  // outputs:
  signal output message;

  message <== Poseidon(1)([messageSeed]);
}
```

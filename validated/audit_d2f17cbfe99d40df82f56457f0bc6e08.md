Confirmed — `MainEVMCircuitMin` proves nothing about fund ownership: it only outputs `Poseidon(messageSeed)` from a public `calldataHash` and `outTimeStamp`. This is the "min" proof path used whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0` [1](#0-0) [2](#0-1) . Any unprivileged EOA can trivially generate a valid witness/proof for this circuit (pick any `messageSeed`, compute Poseidon hash) with no nullifiers spent and no UTXO ownership required.

### Title
Unauthenticated arbitrary `call` in `EmporiumUpgradeable.runAction` drains tokens held by the Emporium contract from other users' in-flight/staged deposits - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes attacker-supplied `(endpoint, callData, value)` operations via a raw `.call` whenever `stack.signerAddress == address(0)`, because `verifyWallet` skips all signature verification in that branch. Combined with the zero-cost `MainEVMCircuitMin` proof path (which requires no real fund ownership), an unprivileged EOA can submit a `transact()` call whose `EmporiumStack` contains a malicious operation (e.g. `ERC20.transfer(attacker, amount)`) that Emporium executes as itself, draining any ERC20 balance the Emporium contract is currently holding — including funds belonging to other users' unfinished multi-step Emporium interactions.

### Finding Description
`EmporiumUpgradeable.runAction` decodes an `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and calls `verifyWallet(stack, circomData)` [3](#0-2) .

`verifyWallet` returns immediately, with no signature check at all, when `stack.signerAddress == address(0)`: [4](#0-3) 

Back in `runAction`, since `stack.signerAddress == address(0)`, the "Stateful Interaction" branch (`op.invokeWallet && stack.signerAddress != address(0)`) is never taken, so every op falls into "CASE 2: Stateless Interaction", which performs an arbitrary raw call with attacker-controlled `endpoint` and `callData` (only `callHinkalWallet`/`doSendToRelay` selectors are blocked): [5](#0-4) 

This call executes with `msg.sender == EmporiumUpgradeable` — i.e., it can invoke `transfer`/`approve`/any function on any token the Emporium contract itself holds or has approved, moving Emporium's own balance out.

Two properties in this codebase make the attack reachable by an unprivileged EOA with no real funds and no other user's key:
1. The `EmporiumStack` (endpoint/callData/signerAddress) is only bound into `circomData.calldataHash` via `getHashedCalldata1` [6](#0-5) , and the on-chain check only verifies `getHashedCalldata(circomData) == circomData.calldataHash` [7](#0-6) . Nothing ties the arbitrary `endpoint`/`callData` to ownership of any specific UTXO/nullifier.
2. When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, the SNARK public input set collapses to `formInputEmporiumMin` (`emporiumMessage`, `timeStamp`, `calldataHash` only) [8](#0-7) , verified against `MainEVMCircuitMin`, which proves nothing except a Poseidon hash of an arbitrary private `messageSeed` — no nullifier spend, no proof of any real deposit [1](#0-0) . Any EOA can generate this proof for free.

The Emporium design intentionally allows funds to remain in the contract across calls — this is confirmed by the balance-accounting comment: "the only case when balanceChange can be < 0, when there were some funds on emporium before the call" and `handleOut` only transfers out and creates a UTXO when `balanceChange > 0`, otherwise leaving the balance sitting in the contract [9](#0-8) . So legitimate multi-step flows (deposit now, act later) leave real user balances resident on the Emporium contract between transactions — exactly the balance an attacker's unauthenticated `CASE 2` call can sweep.

The post-loop balance equality check only inspects tokens present in the attacker's own `circomData.erc20TokenAddresses` array and requires `balanceChange >= 0` for those [10](#0-9) . An attacker can submit an empty/irrelevant `erc20TokenAddresses` (as required for the `EmporiumMin` path) while the malicious `op.callData` drains a *different* token entirely, so no accounting check ever observes the theft.

This breaks the equality the report's bug class targets: a value-bearing state (Emporium's ERC20 balance, belonging to another user's staged deposit) is moved by an unauthorized, unauthenticated call that the CircomData/proof system never actually ties to authorization over that value — i.e., "a transferFrom / wallet op not authorised by the prover or signer."

### Impact Explanation
This is theft of user funds held by the protocol's Emporium external-action contract — funds belonging to other users mid multi-step operation. Per the severity rubric this is at minimum High ("theft or permanent freezing of protocol/relay fees, temporary freezing of user funds, executing calls or moving assets a wallet owner or prover never authorised"), and arguably Critical since it is direct theft of user funds resident in the Emporium contract with no signature or ownership requirement whatsoever.

### Likelihood Explanation
High. No privileged role, relayer cooperation, or victim's private key is required. The attacker needs only:
1. A cheap, self-generated `MainEVMCircuitMin` proof (no real UTXO ownership needed).
2. Knowledge that Emporium currently holds a nonzero balance of some ERC20 token (observable on-chain via `balanceOf`).
3. Craft `EmporiumStack.ops[0] = {endpoint: token, invokeWallet:false, value:0, callData: transfer(attacker, balance)}` and `signerAddress = address(0)`.

### Recommendation
- Never skip signature verification purely based on `signerAddress == address(0)`; require every `EmporiumOperation` to be authorized either by a valid EIP-712 signature from a real signer or restricted to a hardcoded/whitelisted set of endpoints and selectors (e.g., only allow calls whose target is one of `circomData.erc20TokenAddresses` and whose effect is fully captured by the pre/post balance accounting).
- Disallow or heavily restrict the "EmporiumMin"/`MainEVMCircuitMin` proof path from being able to trigger arbitrary `CASE 2` calls; require the full ownership-proving circuit whenever an Emporium operation moves value.
- Ensure the post-operation balance/UTXO accounting in `runAction` covers *all* tokens the operation could have touched, not just `circomData.erc20TokenAddresses`, or forbid Emporium from ever holding cross-transaction balances that aren't owned by a specific nullifier-verified party.

### Proof of Concept
1. Attacker observes `EmporiumUpgradeable` holds `1000 USDC` left over from another user's earlier staged deposit (balance stayed in contract per `handleOut` semantics).
2. Attacker generates a trivial `MainEVMCircuitMin` proof with `erc20TokenAddresses = []`, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, arbitrary `messageSeed`.
3. Attacker builds `EmporiumStack`:
   - `signerAddress = address(0)`
   - `ops = [{ endpoint: USDC_ADDRESS, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, 1000e6)) }]`
4. Attacker calls `Hinkal.transact(...)` with this `circomData`; `performHinkalChecks` passes (calldataHash matches, minimal circuit verifies), `_externalTransact` calls `EmporiumUpgradeable.runAction`.
5. `verifyWallet` returns immediately (signerAddress is zero) [11](#0-10) .
6. `op.endpoint.call(op.callData)` executes `USDC.transfer(attacker, 1000e6)` with `msg.sender = Emporium`, transferring the other user's 1000 USDC to the attacker [12](#0-11) .
7. Since `USDC` is not in the attacker's (empty) `circomData.erc20TokenAddresses`, the balance-equality loop never notices the loss.

### Citations

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-89)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );

        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
        for (uint256 i = 0; i < stack.ops.length; i++) {
            EmporiumOperation memory op = stack.ops[i];

            bool success;
            bytes memory err;

            // CASE 1: Stateful Interaction
            if (op.invokeWallet && stack.signerAddress != address(0)) {
                (success, err) = IHinkalWallet(stack.signerAddress)
                    .callHinkalWallet(op.endpoint, op.callData, op.value);
            }
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

            if (!success) {
                revert CallFailed(err);
            }
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L132-151)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L162-184)
```text
    function handleOut(
        int256 balanceChange,
        CircomData calldata circomData,
        uint256 i
    ) internal returns (UTXO memory outUtxo) {
        // total change can be less than zero if there was some balance before the call -> that's why we have <=
        if (balanceChange <= 0) {
            return outUtxo;
        }

        transferERC20TokenOrETH(
            circomData.erc20TokenAddresses[i],
            msg.sender,
            uint256(balanceChange)
        );

        outUtxo = UTXO(
            uint256(balanceChange),
            circomData.erc20TokenAddresses[i],
            circomData.stealthAddressStructure,
            circomData.timeStamp
        );
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-317)
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

**File:** contracts/HinkalHelper.sol (L208-226)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
```

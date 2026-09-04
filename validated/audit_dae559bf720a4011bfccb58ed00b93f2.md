### Title
Emporium min-proof path skips both balance-accounting and signature auth, allowing unauthenticated arbitrary calls that drain funds held by the Emporium contract - (File: contracts/CircomDataBuilder.sol, contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only constrains `message == Poseidon(messageSeed)`, `timeStamp`, and `calldataHash` [1](#0-0) , with no root-hash, nullifier, or amount binding (matching `MainEVMCircuitMin`, which has exactly those three signals) [2](#0-1) . Combined with `EmporiumUpgradeable.verifyWallet` skipping the EIP-712 signature check entirely when `stack.signerAddress == address(0)` [3](#0-2) , an attacker gets a fully unauthenticated call path into `runAction`'s op-execution loop, which performs arbitrary `op.endpoint.call{value: op.value}(op.callData)` from the Emporium contract's own identity [4](#0-3) .

### Finding Description
The claimed broken equality is: *assets Emporium can move in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`*. This equality is broken because the accounting loop in `runAction` is indexed by `circomData.erc20TokenAddresses`, which the attacker sets to length 0 to trigger the min-proof path [5](#0-4) [6](#0-5) . With this array empty, `balancesBefore`/`balancesAfter` are empty arrays, `deltaAmountChanges` is sized to 0 in `_externalTransact` [7](#0-6) , and the post-loop accounting/UTXO-creation logic (lines 132-151) never executes — meaning **nothing** constrains what the op loop is allowed to move.

Separately, authorization normally comes from two possible sources: (1) a signature over the ops signed by `stack.signerAddress` via EIP-712 (`verifyWallet`), or (2) proof of ownership of the UTXOs/funds being moved, enforced through the full `MainEVMCircuit` (root hash, nullifiers, `amountChanges`) when `erc20TokenAddresses.length > 0`. The attacker's construction defeats both simultaneously:
- Setting `signerAddress == address(0)` makes `verifyWallet` return immediately after only marking the message as used — no signature is checked at all [8](#0-7) .
- Setting `erc20TokenAddresses.length == 0` selects `formInputEmporiumMin`, which requires only knowledge of an arbitrary `messageSeed` (something anyone can freely generate; no secret UTXO knowledge is needed) [9](#0-8) [2](#0-1) .

With both guards defeated, the attacker calls `Hinkal.transact` with a valid (trivial) min-proof and an `externalActionMetadata` decoding to an `EmporiumStack{ signerAddress: address(0), ops: [{ endpoint: <attacker or token>, invokeWallet: false, value: X, callData: <arbitrary, e.g. ERC20.transfer(attacker, amount) or empty for raw ETH> }] }`. Inside `runAction`'s stateless branch, the only restriction is that the callData selector must not be `callHinkalWallet`/`doSendToRelay` [10](#0-9) , which does not prevent a raw ETH transfer or an arbitrary ERC20 call originating from the Emporium contract's own balance (since `msg.sender` inside that low-level `.call` is `EmporiumUpgradeable`, which is the actual holder of any parked/in-flight ETH or ERC20 balance). Since `circomData.erc20TokenAddresses` is empty, none of this movement is checked against `balancesBefore`/`balancesAfter`, `slippageValues` in `Hinkal.transact`, or the `BalanceChangeShouldBePositive` guard — those loops simply never execute for an empty array.

This matches the described flaw precisely: the min-circuit was intended for stateless/self-authorized (signed) actions that don't move Hinkal-accounted balances, but the code does not enforce that `signerAddress != address(0)` whenever the min-proof path (`erc20TokenAddresses.length == 0`) is used. This lets an attacker pick the one combination (`signerAddress == 0` AND `erc20TokenAddresses.length == 0`) that eliminates both forms of authorization simultaneously.

### Impact Explanation
Any funds sitting in the `EmporiumUpgradeable` contract's own balance (ETH or ERC20 — "parked" balances from prior deposits, in-flight multi-step DeFi legs, or any dust/leftover from other users' Emporium operations) can be moved out by an arbitrary unprivileged attacker via a fully-controlled external call, with zero signature check and zero balance/slippage/UTXO accounting. This is direct theft of shielded or in-flight user funds — Critical severity, matching the rules' Critical category. The attack is repeatable each time the Emporium contract holds any balance, limited only by generating a fresh `emporiumMessage`/proof per transaction (cheap and fully attacker-controlled, no secret needed).

### Likelihood Explanation
Preconditions: the Emporium contract must hold some ETH/ERC20 balance at the time of attack (e.g., during multi-step operations where funds are parked between steps, or leftover dust from slippage/rounding in prior legs). Attacker cost is minimal — generating a Groth16 proof for the trivial `MainEVMCircuitMin` circuit requires no secret input tied to any other user, only an arbitrary self-chosen `messageSeed`. Constructing the `EmporiumStack` calldata is fully within attacker control (`externalActionMetadata` is attacker-supplied). No privileged role, relay cooperation, or victim key is required. This is fully self-serviceable by any EOA that can call `Hinkal.transact`.

### Recommendation
Enforce that the Emporium min-proof path can only be used when `stack.signerAddress != address(0)` (i.e., require a valid signed authorization for any op execution when `erc20TokenAddresses.length == 0`), or alternatively disallow selecting `formInputEmporiumMin` unless the decoded `EmporiumStack.signerAddress` is non-zero and its signature is verified before any op runs. Additionally, consider restricting stateless (`invokeWallet == false`, `signerAddress == address(0)`) calls to a bounded allowlist of endpoints/selectors, since these calls execute directly from the Emporium contract's identity and can otherwise move any asset the contract holds regardless of `erc20TokenAddresses` length.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as an allowed external action, `externalActionMap[HINKAL_EMPORIUM_ACTION_ID] = emporiumAddress`), and a mock ERC20/verifier.
2. Fund `EmporiumUpgradeable` directly with ETH (e.g., `vm.deal(address(emporium), 10 ether)`) and/or mint ERC20 tokens to it, simulating "parked balance."
3. As an unprivileged attacker EOA (no deposits, no UTXOs), construct `CircomData` with: `externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, `externalActionData.externalActionMetadata = abi.encode(EmporiumStack({signerAddress: address(0), ops: [EmporiumOperation({endpoint: attacker, invokeWallet: false, value: 10 ether, callData: ""})], maxFee: 0, deadline: type(uint256).max, v:0, r:0, s:0}))`.
4. Generate a locally-produced Groth16 proof for `MainEVMCircuitMin` with an arbitrary `messageSeed`, setting `emporiumMessage = Poseidon(messageSeed)`, matching `calldataHash`/`timeStamp` per `getHashedCalldata`.
5. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from the attacker EOA with no `msg.value`.
6. Assert: `address(emporium).balance` before == 10 ether, after == 0; `attacker.balance` increases by 10 ether. Assert this happened despite `circomData.erc20TokenAddresses.length == 0` (i.e., `balancesBefore.length == balancesAfter.length == 0`), proving assets moved with zero entries accounted for — breaking the stated invariant that "assets Emporium can move in a tx == assets accounted in balancesBefore/balancesAfter."

### Citations

**File:** contracts/CircomDataBuilder.sol (L134-161)
```text
    function formInputForCircom(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory) {
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
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

**File:** contracts/Hinkal.sol (L244-256)
```text
        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }
```

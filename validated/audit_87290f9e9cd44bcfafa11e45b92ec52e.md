## Verdict: Valid vulnerability confirmed

The claim is well-supported by the code. I traced the equality the question implies — **"assets Emporium can move in a tx == assets accounted in balancesBefore/balancesAfter"** — and confirmed it is broken when `erc20TokenAddresses.length == 0`.

### Title
Emporium min-circuit path allows unaccounted arbitrary calls draining Emporium's held funds - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
When an attacker calls `Hinkal.transact` with `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and `erc20TokenAddresses.length == 0`, `formInputForCircom` routes to `formInputEmporiumMin`, which only requires proving `message == Poseidon(messageSeed)` — a trivial, self-satisfiable statement with no binding to nullifiers, roots, or the `EmporiumStack` ops. Combined with `EmporiumUpgradeable.runAction`'s balance-accounting loop iterating over the (empty) `erc20TokenAddresses` array, and `verifyWallet` skipping all signature checks when `stack.signerAddress == address(0)`, an attacker can execute arbitrary, unauthenticated `call()`s from Emporium's identity with zero accounting.

### Finding Description
`dimensionsCheck` in [1](#0-0)  forces `erc20TokenAddresses.length == dimensions.tokenNumber == amountChanges.length == inputNullifiers.length == outCommitments.length`, so an attacker can legally submit an all-zero-length `CircomData` (no UTXOs, no nullifiers, no outputs).

With `erc20TokenAddresses.length == 0` and `externalActionId == HINKAL_EMPORIUM_ACTION_ID`, `formInputForCircom` selects `formInputEmporiumMin`: [2](#0-1) . The circuit it targets, `MainEVMCircuitMin`, only constrains `message <== Poseidon([messageSeed])` and never uses `outTimeStamp`/`calldataHash` in any constraint: [3](#0-2) . Anyone can pick their own `messageSeed` and produce a valid proof — no secret, root, or nullifier knowledge required. The root-hash check in `Hinkal.transact` (`rootHashExists`) is satisfied trivially with any historical public root, independent of nullifier count.

Inside `EmporiumUpgradeable.runAction`, `verifyWallet` returns immediately with **no signature check at all** when `stack.signerAddress == address(0)`: [4](#0-3) . The op-execution loop then performs an unauthenticated, attacker-controlled `op.endpoint.call{value: op.value}(op.callData)` from Emporium's own address: [5](#0-4) . Both `balancesBefore`/`balancesAfter` and the accounting loop that would normally catch unauthorized balance movement iterate over `circomData.erc20TokenAddresses`: [6](#0-5) . When that array is empty, this loop is a no-op — any token or ETH movement the op triggers (e.g., `transfer`, `approve`, or draining `receive()`-accumulated ETH) is completely unaccounted for.

`onlyAllowedRecipient` only gates *who calls* `runAction` (i.e., that the caller is the registered Hinkal/Emporium wiring): [7](#0-6)  — it does not constrain the contents of `EmporiumStack.ops`, which the attacker fully controls via `externalActionData.externalActionMetadata`.

### Impact Explanation
Any ETH or ERC20 balance transiently or permanently held by the Emporium contract (from `receive()`, in-flight multi-leg swap intermediates, dust from prior partial operations, or relay-fee remainders) can be stolen outright by an unprivileged attacker in a single transaction, with a near-free, self-generated Min-circuit proof and no signature or accounting check. This matches Critical: direct theft of shielded/in-flight user funds, and is repeatable every time Emporium accrues a balance.

### Likelihood Explanation
Preconditions are minimal and fully attacker-controlled: submit `erc20TokenAddresses = []`, matching zero-length dimensions, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, any historical valid `rootHashHinkal`, a self-chosen `messageSeed`/`emporiumMessage`, and an `EmporiumStack` with `signerAddress = address(0)` and an op targeting whatever token/ETH Emporium holds. No relay, admin, or victim cooperation is needed. Feasibility depends only on Emporium actually holding a nonzero balance at call time, which is plausible given its `receive()` fallback and its role as an intermediate holder during multi-op/swap flows.

### Recommendation
Do not allow the Min/empty-token-array path to bypass balance accounting for `HINKAL_EMPORIUM_ACTION_ID`: require `erc20TokenAddresses` to include every token address touched by `stack.ops` (or otherwise snapshot Emporium's full balance, e.g., of `msg.value`-relevant assets and any token referenced in `op.callData`) before/after execution regardless of array length. Additionally, disallow `verifyWallet` from silently skipping all authorization when `signerAddress == address(0)` unless the op set is provably restricted to actions that cannot move value out of Emporium.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium under `HINKAL_EMPORIUM_ACTION_ID`, and register a Min-circuit verifier for the corresponding `buildVerifierId(dimensions{0,0,0}, HINKAL_EMPORIUM_ACTION_ID)`.
2. Fund Emporium directly with an ERC20 balance (simulating dust/in-flight funds) — assert `token.balanceOf(emporium) == X`.
3. As an attacker EOA, generate a local Min-circuit proof for a self-chosen `messageSeed` (no relation to any UTXO).
4. Build `CircomData` with `erc20TokenAddresses = []`, `dimensions = {0,0,0}`, `externalActionData.externalActionMetadata` encoding an `EmporiumStack{signerAddress: address(0), ops: [{endpoint: token, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (attacker, X))}]}`.
5. Call `Hinkal.transact(...)`.
6. Assert `token.balanceOf(attacker) == X` and `token.balanceOf(emporium) == 0`, proving theft occurred with zero UTXOs/nullifiers spent and zero accounting performed — i.e., assets moved by Emporium ≠ assets accounted in `balancesBefore`/`balancesAfter` (both empty arrays).

### Citations

**File:** contracts/HinkalHelper.sol (L64-71)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
```

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-151)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );

        verifyWallet(stack, circomData);

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

        payRelayFees(circomData, stack.signerAddress, deltaAmountChanges);

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

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L39-46)
```text
    modifier onlyAllowedRecipient() {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();
        require(
            $._isAllowedRecipient[msg.sender],
            "ExternalActionBase: sender not allowed"
        );
        _;
    }
```

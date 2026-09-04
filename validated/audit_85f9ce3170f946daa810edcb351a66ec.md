### Title
Emporium `runAction` skips all authorization when `signerAddress == address(0)`, letting the zero-constraint "Min" proof drive arbitrary calls from Emporium's identity - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
When `formInputForCircom` routes an Emporium action with an empty token array to `formInputEmporiumMin`, the resulting Groth16 public inputs constrain nothing but `emporiumMessage`, `timeStamp` and `calldataHash` — no UTXO ownership, nullifier, or root-hash checks are present. Combined with `EmporiumUpgradeable.verifyWallet` completely skipping ECDSA verification when `EmporiumStack.signerAddress == address(0)`, an unprivileged caller can make Emporium execute an arbitrary `op.endpoint.call(op.callData)` (e.g. `approve(attacker, type(uint256).max)`) from Emporium's own identity, with zero balance accounting since the loop only iterates the (empty) `erc20TokenAddresses` array.

### Finding Description
The broken equality is: *assets Emporium can move/authorize in a transaction == assets accounted for in `balancesBefore`/`balancesAfter`*.

- `formInputForCircom` selects `formInputEmporiumMin` whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID && erc20TokenAddresses.length == 0`: [1](#0-0) 
- `formInputEmporiumMin` produces only 3 public signals (`emporiumMessage`, `timeStamp`, `calldataHash`) — no root hash, no nullifiers, no amount changes: [2](#0-1) 

Since `emporiumMessage` is any value the attacker chooses and `Poseidon` is a public deterministic function, the attacker can pick their own `messageSeed`, compute `emporiumMessage = Poseidon(messageSeed)`, and trivially generate a valid Min-circuit proof for it. This proof therefore carries no real spending authorization — it merely proves knowledge of a self-chosen preimage.

`EmporiumUpgradeable.runAction` decodes `EmporiumStack` straight from attacker-controlled `externalActionData.externalActionMetadata`: [3](#0-2) 

`verifyWallet` returns immediately, skipping the EIP-712 ECDSA check entirely, when `stack.signerAddress == address(0)`: [4](#0-3) 

The op-execution loop then performs a raw call from the Emporium contract itself for any op that is not `invokeWallet && signerAddress != 0`: [5](#0-4) 

The only guardrail on this raw call is a selector blacklist for `callHinkalWallet`/`doSendToRelay` — an ERC-20 `approve(attacker, max)` call to any token Emporium holds is not blocked. The balance-accounting loop that would otherwise catch unaccounted balance movement only iterates `circomData.erc20TokenAddresses`, which is required to be empty for this proof path to be selected, so it cannot detect anything happening on other tokens; and `approve` does not itself change Emporium's own balance, so even a non-empty accounting for that particular token would not flag the exploit: [6](#0-5) 

`HinkalHelper.performHinkalChecks`'s `calldataHash` equality check only proves the attacker's own submitted `externalActionData` was not tampered with by a relay — it places no restriction on what values the attacker (as `originalSender`) may put in `EmporiumStack`: [7](#0-6) 

`onlyAllowedRecipient` on `EmporiumUpgradeable.runAction` restricts direct callers to the whitelisted `Hinkal` dispatcher, but `Hinkal.transact` itself is a permissionless entrypoint any EOA can call: [8](#0-7) 

Exploit flow: attacker calls `Hinkal.transact` with `externalActionData.externalAddress = Emporium`, `externalActionId = HINKAL_EMPORIUM_ACTION_ID`, `erc20TokenAddresses = []`, a self-generated valid Min proof for a self-chosen `emporiumMessage`, and `externalActionMetadata` encoding an `EmporiumStack{ signerAddress: address(0), ops: [{endpoint: <token Emporium holds>, invokeWallet:false, value:0, callData: approve(attacker, type(uint256).max)}] }`. Emporium executes the approval with its own identity, no signature check, and no balance accounting. Attacker then calls `token.transferFrom(emporium, attacker, balance)` outside of Hinkal to drain any ERC-20 balance Emporium holds (residual/in-flight/fee funds).

The question's framing around "maximum allowed array lengths / off-by-one" was not substantiated during review — the vulnerability does not depend on array-length boundary conditions; it is a straightforward authorization bypass for the `signerAddress == address(0)` branch that exists at any array length, including zero.

### Impact Explanation
Any ERC20 (or ETH, via `op.value`/other calls) balance held by the `EmporiumUpgradeable` contract — whether from in-flight multi-step transactions, protocol fee accrual, or dust — can be fully drained by an unprivileged attacker, matching Critical: direct theft of shielded/in-flight user funds. The attack is repeatable for every token/asset Emporium ever custodies and costs the attacker only gas plus trivial proof generation.

### Likelihood Explanation
Preconditions: Emporium must hold a non-zero balance of some asset at the time of attack (a normal, expected transient state for a contract that stages multi-step swaps/executions). No tree state, no privileged role, and no signature from any legitimate signer are required. The attacker only needs the ability to call the public `Hinkal.transact` entrypoint and generate a Min-circuit proof for a self-chosen message, which is possible for any address. This makes the attack highly likely and cheap once Emporium holds any balance.

### Recommendation
Do not allow `EmporiumUpgradeable.runAction` to skip signer verification when `signerAddress == address(0)`; either require an authenticated signer for every op, or restrict the zero-signer path to a narrowly scoped, non-arbitrary set of pre-approved operations. Additionally, the Min proof path should be restricted to actions that provably cannot move or approve any asset (e.g., disallow arbitrary `op.endpoint`/`op.callData` combinations, or require the full `formInputNormal` path — with real UTXO/root/nullifier constraints — whenever `EmporiumStack.ops` contains any state-changing external call).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable` (as an allowed recipient), and a mock ERC20. Fund `EmporiumUpgradeable` directly with `mockToken.mint(emporium, 1000e18)` to simulate in-flight/residual balance.
2. As attacker EOA (no special role), pick `messageSeed`, compute `emporiumMessage = Poseidon(messageSeed)` locally, and generate a valid Min-circuit Groth16 proof (`mainEVMCircuitMin0v4`/`VerifierEVMMin0v4`) attesting only to that Poseidon relation.
3. Build `CircomData` with `erc20TokenAddresses = []`, `externalActionData = {externalAddress: emporium, externalActionId: HINKAL_EMPORIUM_ACTION_ID, externalActionMetadata: abi.encode(EmporiumStack{signerAddress: address(0), ops: [{endpoint: mockToken, invokeWallet:false, value:0, callData: abi.encodeCall(IERC20.approve,(attacker, type(uint256).max))}], maxFee:0, deadline:0, v:0,r:0,s:0})}`, and `calldataHash` computed via `getHashedCalldata`.
4. Call `Hinkal.transact(...)` from attacker EOA with the proof and this `circomData`.
5. Assert `mockToken.allowance(emporium, attacker) == type(uint256).max`, then call `mockToken.transferFrom(emporium, attacker, 1000e18)` and assert `mockToken.balanceOf(attacker) == 1000e18` and `mockToken.balanceOf(emporium) == 0`, proving assets moved without being accounted in `balancesBefore`/`balancesAfter` (both empty since `erc20TokenAddresses.length == 0`).

### Citations

**File:** contracts/CircomDataBuilder.sol (L139-148)
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
```

**File:** contracts/CircomDataBuilder.sol (L150-161)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-157)
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

        if (utxoSetLength < circomData.erc20TokenAddresses.length) {
            utxoSet.skipLast(
                circomData.erc20TokenAddresses.length - utxoSetLength
            );
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

**File:** contracts/HinkalHelper.sol (L208-236)
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
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
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

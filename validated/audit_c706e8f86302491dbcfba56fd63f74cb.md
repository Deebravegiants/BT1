### Title
Forged nested `CircomData` in `EmporiumUpgradeable.runAction`'s stateless op lets an attacker drain any `DepositOnChainUtxosExternalAction`-approved victim - ([File: contracts/external-actions/DepositOnChainUtxosExternalAction.sol])

### Finding Description
The equality claimed to be broken: **`msg.sender` inside `DepositOnChainUtxosExternalAction.runAction` == `hinkalAddress`** (i.e., the only caller of any `IExternalActionV2.runAction` should be `Hinkal` itself, and any `CircomData` reaching it should be the proof-checked struct from `Hinkal._externalTransact`, [1](#0-0) ).

Trace: `Hinkal.transact` first calls `hinkalHelper.performHinkalChecks(circomData, dimensions, msg.sender)`, which enforces `circomData.originalSender == msg.sender` (when `relay==0`) and validates `calldataHash`, before `verifyProof` and `_externalTransact` run [2](#0-1) . When the external action is `EmporiumUpgradeable`, `Hinkal._externalTransact` invokes `EmporiumUpgradeable.runAction(circomData, deltaAmountChanges)` with that already-checked `circomData` [1](#0-0) . Inside `EmporiumUpgradeable.runAction`, for a "stateless interaction" op the contract performs a raw low-level call: `op.endpoint.call{value: op.value}(op.callData)` [3](#0-2) . Both `op.endpoint` and `op.callData` are fully attacker-controlled fields decoded from `circomData.externalActionData.externalActionMetadata` (the `EmporiumStack`) [4](#0-3) .

If `op.endpoint = DepositOnChainUtxosExternalAction` and `op.callData = abi.encodeWithSelector(runAction.selector, forgedCircomData, [0,...])`, this reaches `DepositOnChainUtxosExternalAction.runAction` with `msg.sender == Emporium` (not `Hinkal`), and with a completely new, forged `CircomData` struct that was never passed through `hinkalHelper.performHinkalChecks`. The `onlyAllowedRecipient` modifier only checks `isAllowedRecipient[msg.sender]` [5](#0-4) ; if Emporium is on that allow-list, this check passes trivially. Inside, `userAddress = circomData.originalSender` is taken directly from the *forged* struct with no constraint tying it to the real transacting user, and `transferERC20TokenFrom(tokenAddress, userAddress, msg.sender, tokenTotal)` performs `IERC20.safeTransferFrom(userAddress, Emporium, tokenTotal)` [6](#0-5) . The only requirement for this to succeed is that `userAddress` has an ERC20 allowance for the `DepositOnChainUtxosExternalAction` contract address (the actual `msg.sender` at the ERC20 level is always `address(this)` regardless of who called `runAction`) — a normal precondition for any past legitimate user of the on-chain-UTXO-deposit feature. In the *legitimate* path (`Hinkal → DepositOnChainUtxosExternalAction` directly), `performHinkalChecks` forces `originalSender == msg.sender` of the outer call, so a user can only ever pull their own tokens. That guard is completely bypassed for the nested/forged call because `performHinkalChecks` runs exactly once, on the *outer* `circomData`, and never re-validates the inner forged struct decoded inside `EmporiumUpgradeable.runAction`'s op loop. The `calldataHash` check only certifies that the attacker's own submitted bytes match what their own proof committed to — it does not constrain the *semantic content* of the nested `CircomData` (e.g., that its `originalSender` equal the real caller).

The stolen tokens land in Emporium's balance, and are then swept into new UTXOs by Emporium's own accounting (`balanceChange` computed from `balancesBefore/After` and turned into `handleOut(...)` UTXOs credited per the *attacker's own, self-controlled* `circomData.stealthAddressStructure`/output commitments) [7](#0-6) , i.e., the attacker's own valid proof lets them claim the pulled victim funds as their own private UTXO.

### Impact Explanation
Critical — this is a proof/authorization bypass allowing state-changing ERC20 `transferFrom` pulls of victim funds without the victim's proof or consent, converting them into attacker-owned shielded UTXOs. It is fully repeatable against any address that has ever granted (and not revoked) an allowance to `DepositOnChainUtxosExternalAction`, matching the "direct theft of shielded or in-flight user funds" / "proof verification bypass" Critical category.

### Likelihood Explanation
This requires one non-attacker-controlled precondition: **Emporium must be present in `DepositOnChainUtxosExternalAction`'s `isAllowedRecipient` mapping**, set via `setAllowedRecipients`, which is an `onlyOwner` action on `DepositOnChainUtxosExternalAction` [8](#0-7) . I was unable to find any deployment script, config, or test file in the indexed codebase that actually registers Emporium as an allowed recipient of `DepositOnChainUtxosExternalAction`, nor any reference showing these two contracts are wired together in the deployed system (my searches for `DepositOnChainUtxosExternalAction` usages, `setAllowedRecipients` calls, and deploy scripts returned no hits beyond the contract's own source). Given the size limits on the indexed codebase, I cannot rule out that such wiring exists in deploy scripts/config that weren't indexed — the user should verify this precondition against the actual deployment configuration, potentially by starting a Devin session with full repository access, before treating this as an exploitable-in-production bug. If Emporium is never granted this permission, the attack path described does not exist, and this reduces to a purely theoretical, non-actionable code-pattern observation (the "any external action can be driven with attacker-crafted `CircomData` by any other allow-listed action contract" pattern is real but requires that specific misconfiguration).

### Recommendation
- `DepositOnChainUtxosExternalAction` (and any `ExternalActionBaseV2`/`ExternalActionBaseUpgradeable` action) should never accept `isAllowedRecipient` for anything other than the canonical `Hinkal` contract address — enforce a single, immutable `hinkalAddress` check (`msg.sender == hinkalAddress`) instead of an owner-mutable allow-list, closing off the possibility of one external action contract legitimately invoking another's `runAction`.
- If cross-action composition via Emporium's stateless ops is an intended feature, `EmporiumUpgradeable.runAction`'s stateless branch must not be allowed to call other `ExternalActionBaseV2`/`IExternalActionV2.runAction` implementations with attacker-supplied `CircomData`; explicitly block calls whose selector matches `IExternalActionV2.runAction.selector`, mirroring the existing `UnauthorizedWalletCall` guard for `callHinkalWallet`/`doSendToRelay` [3](#0-2) .
- Audit the current `setAllowedRecipients` configuration on all deployed `ExternalActionBaseV2`/`ExternalActionBaseUpgradeable` contracts to confirm Emporium (or any other external action contract) is not present in another action's allow-list.

### Proof of Concept
Hardhat fork test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `DepositOnChainUtxosExternalAction` (with `allowedRecipients = [HinkalAddress]` initially), `EmporiumUpgradeable`, and a mock ERC20.
2. Have `victim` `approve(DepositOnChainUtxosExternalAction, largeAmount)` on the ERC20 (simulating a past legitimate on-chain-deposit user), without victim ever interacting again.
3. As `owner`, call `DepositOnChainUtxosExternalAction.setAllowedRecipients([EmporiumAddress])` to realize the stated precondition.
4. As `attacker`, register `EmporiumUpgradeable` under `Hinkal.registerExternalAction(EMPORIUM_ACTION_ID, EmporiumAddress)`.
5. Attacker builds their own outer `circomData` (with `originalSender = attacker`, valid `calldataHash`, and a genuine proof for their own deposit/withdraw amounts) whose `externalActionData.externalActionMetadata` encodes an `EmporiumStack` containing one stateless `EmporiumOperation` with `endpoint = DepositOnChainUtxosExternalAction`, `invokeWallet = false`, `callData = abi.encodeWithSelector(DepositOnChainUtxosExternalAction.runAction.selector, forgedCircomData, [0])` where `forgedCircomData.originalSender = victim` and `erc20TokenAddresses = [token]`.
6. Call `Hinkal.transact(a, b, c, dimensions, circomData)` from `attacker`.
7. Spy/mock `hinkalHelper.performHinkalChecks` to record its call count and argument `circomData` hashes; assert it was called exactly once (for the outer `circomData`) and never with `forgedCircomData`.
8. Assert `runAction` on `DepositOnChainUtxosExternalAction` executed successfully (`BlockedUtxosCreated` event emitted) and `token.allowance(victim, DepositOnChainUtxosExternalAction)` decreased by `tokenTotal` while `victim`'s balance decreased accordingly, with no signature/proof ever submitted by `victim`.
9. Assert Emporium's resulting UTXO output (from `handleOut`) is attributed to the attacker's stealth address / output commitments, confirming the equality **"every `runAction` caller == Hinkal, and every `CircomData` reaching `runAction` has passed `performHinkalChecks` for the actual token owner"** is false both in code path (msg.sender==Emporium) and in effect (victim funds moved without victim's `performHinkalChecks` invocation).

### Citations

**File:** contracts/Hinkal.sol (L234-261)
```text
    function _externalTransact(
        CircomData calldata circomData
    ) internal returns (UTXO[] memory) {
        require(
            externalActionMap[circomData.externalActionData.externalActionId] ==
                circomData.externalActionData.externalAddress &&
                circomData.externalActionData.externalAddress != address(0),
            "Unknown externalAddress"
        );

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

        return
            IExternalActionV2(circomData.externalActionData.externalAddress)
                .runAction(circomData, deltaAmountChanges);
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-150)
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
```

**File:** contracts/external-actions/emporium/EmporiumStack.sol (L1-19)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.17;

struct EmporiumOperation {
    address endpoint;
    bool invokeWallet;
    uint128 value;
    bytes callData;
}

struct EmporiumStack {
    uint8 v;
    bytes32 r;
    bytes32 s;
    address signerAddress;
    EmporiumOperation[] ops;
    uint256 maxFee;
    uint256 deadline;
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

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L30-37)
```text
    function setAllowedRecipients(
        address[] calldata recipients
    ) external onlyOwner {
        for (uint i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "zero address!");
            isAllowedRecipient[recipients[i]] = true;
        }
    }
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L31-82)
```text
        address userAddress = circomData.originalSender;
        require(
            userAddress != address(0),
            "DepositOnChainUtxosExternalAction: Invalid originalSender"
        );

        uint256[][] memory utxoAmounts = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (uint256[][])
        );
        require(
            utxoAmounts.length == tokenCount,
            "DepositOnChainUtxosExternalAction: metadata length mismatch"
        );

        utxoSet = new UTXO[](countUtxos(utxoAmounts));

        uint256 utxoIndex = 0;
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );

            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
```

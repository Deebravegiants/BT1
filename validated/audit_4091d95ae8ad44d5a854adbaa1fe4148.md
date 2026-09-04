## Answer

This is a valid, confirmed critical vulnerability.

### Title
Unlisted tokens accumulated at the shared Emporium contract can be drained by any subsequent unprivileged caller via CASE 2 - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` only reconciles balance changes for tokens listed in `circomData.erc20TokenAddresses` (via `getBalancesForArray`), but CASE 2 ("Stateless Interaction") allows arbitrary `op.endpoint.call(op.callData)` with no restriction beyond blocking `callHinkalWallet`/`doSendToRelay` selectors. Any ERC20/vault-share/interest-bearing token minted to Emporium's balance by an action whose output token is absent from the caller's declared token list is invisible to the reconciliation loop, sits unattributed in the shared, singleton Emporium contract, and can subsequently be drained by any other unprivileged user who submits their own `transact()` call with a CASE 2 op that directly calls `IERC20(token).transfer(attacker, balance)`.

### Finding Description
Equality claimed: **VALUE_CONSERVATION** — tokens entering/leaving Emporium via an action == the sum of `amountChanges`/UTXOs it produces for the declared `erc20TokenAddresses`. This equality is only checked per-index over `circomData.erc20TokenAddresses` in both `EmporiumUpgradeable.runAction` ( [1](#0-0) ) and in `Hinkal.transact`'s balance-diff check ( [2](#0-1) ). Crucially, that top-level check in `Hinkal.transact` measures **Hinkal's own** balance (`getBalancesForArray` called on `address(this)` = Hinkal), not Emporium's, since Emporium is a separately deployed, registered singleton contract ( [3](#0-2) ). So any token balance change that happens purely inside Emporium and is never listed in `erc20TokenAddresses` is invisible to both checks.

CASE 2 lets an attacker's own action call any `op.endpoint` with any `op.callData`, gated only against the `callHinkalWallet`/`doSendToRelay` selectors: [4](#0-3) . `verifyWallet` performs no signature check at all when `stack.signerAddress == address(0)` (the CASE 2 path), it merely marks the message as used: [5](#0-4) .

Exploit flow:
1. Victim (or attacker acting as depositor) calls `Hinkal.transact` targeting Emporium with `erc20TokenAddresses = [tokenA]`, and a CASE 2 op that calls a lending protocol's `deposit()` converting `tokenA` into a receipt token `tokenX` that is never listed. `runAction`'s reconciliation loop (lines 132-151) only iterates `tokenA`; `tokenX`'s new balance at Emporium is never turned into a UTXO and is not blocked by `BalanceChangeShouldBePositive`, since that check only inspects listed tokens.
2. Emporium (a single shared, upgradeable proxy instance used by all users, gated only by `onlyAllowedRecipient` which permits calls from Hinkal itself: [6](#0-5) ) now holds `tokenX` balance with no on-chain record of ownership.
3. Any other unprivileged attacker calls `Hinkal.transact` with their own valid nullifiers/proof for an unrelated (or even the emporium-min zero-token) circuit path, `erc20TokenAddresses` deliberately excluding `tokenX`, and a CASE 2 op: `endpoint = tokenX`, `callData = abi.encodeCall(IERC20.transfer, (attacker, balanceOfEmporium))`. Because `tokenX` is outside their declared list, neither `balancesBefore/After` diffing nor `BalanceChangeShouldBePositive` (lines 85-151) nor `Hinkal.transact`'s slippage/balance-equation check (lines 97-147, operating on Hinkal's own balance) observe or block this transfer. The call executes with `msg.sender == Emporium`, moving `tokenX` straight to the attacker's EOA, bypassing the UTXO system entirely.

### Impact Explanation
Direct theft of a victim's shielded/in-flight funds parked at a shared external-action contract, with no attribution mechanism — this matches Critical: "direct theft of shielded or in-flight user funds" / "permanent freezing of user funds" (here, freezing converted into theft by an unprivileged third party). The attack is repeatable against every unlisted-token balance that ever accumulates at Emporium, and against every victim who uses CASE 2 to route through any protocol whose output token differs from the declared `erc20TokenAddresses`.

### Likelihood Explanation
Preconditions: some victim (possibly the attacker themself, or an innocent user) must have previously executed an Emporium CASE 2 action whose output token was not included in `erc20TokenAddresses` — an easy and plausible mistake/oversight for any interaction with lending/vault/interest-bearing/NFT-minting protocols, since nothing in the contract enforces that all resulting asset types are declared. The attacker then needs only their own ordinary valid Hinkal proof/nullifiers (any small UTXO, or the zero-token "Emporium min" circuit path enabled by `formInputEmporiumMin` when `erc20TokenAddresses.length == 0`, per `CircomDataBuilder.formInputForCircom`: [7](#0-6) ) and freely crafts the CASE 2 op. No privileged role, relay, or signature is required. Cost is minimal (one transaction + gas); feasibility is high given attacker controls all of `CircomData`, `EmporiumStack`, and calldata per the stated threat model.

### Recommendation
Track and constrain all tokens/assets that Emporium's balance can gain during an action, not just those listed in `erc20TokenAddresses` — e.g., require CASE 2 (and CASE 1) target contracts/output tokens to be declared and reconciled, or restrict `op.endpoint` calls to a controlled allowlist with declared output-token accounting, or snapshot/require zero net-new balance for any token not present in `erc20TokenAddresses` after the ops loop (revert if any un-declared ERC20 balance of Emporium increases). Alternatively, isolate per-transaction execution (e.g., minimal proxy/clone per action) so no shared balance persists across unrelated users' transactions.

### Proof of Concept
Foundry fork test plan:
1. Deploy `Hinkal`, `HinkalHelper`, `EmporiumUpgradeable`, register Emporium as external action and allowed recipient.
2. Deploy a mock lending protocol `MockLending.deposit(tokenA_amount) -> mints tokenX to caller (Emporium)`.
3. Victim calls `transact()` with `erc20TokenAddresses=[tokenA]`, CASE 2 op = `MockLending.deposit(...)`. Assert `tokenX.balanceOf(emporium) > 0` after the tx, and that `tokenX` never appears in any UTXO output/`onChainCommitments`.
4. Attacker (fresh unprivileged EOA with their own trivial valid UTXO/nullifier) calls `transact()` again targeting Emporium, `erc20TokenAddresses` excluding `tokenX`, CASE 2 op = `tokenX.transfer(attacker, tokenX.balanceOf(emporium))`.
5. Assert the second `transact()` succeeds and `tokenX.balanceOf(attacker) == victim's deposited amount`, while `tokenX.balanceOf(emporium) == 0`, proving the equality `tokens entering Emporium == amountChanges/UTXOs produced` is violated and funds are stolen.

### Citations

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

**File:** contracts/Hinkal.sol (L88-147)
```text
            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

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

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
            }
```

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

### Title
Emporium `runAction` bypasses balance-conservation checks when `erc20TokenAddresses` is empty, allowing theft of pooled protocol funds - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`Hinkal.transact()` supports an "Emporium-min" mode where `circomData.erc20TokenAddresses` is empty (used whenever `externalActionId == HINKAL_EMPORIUM_ACTION_ID` and the token list is empty), which drops the entire balance-accounting loop both in `Hinkal.sol` and in `EmporiumUpgradeable.runAction`. In that mode an unprivileged caller with a trivially valid ZK proof (their own, possibly zero-value, UTXOs) can smuggle an arbitrary `EmporiumOperation` (`endpoint`, `callData`) that is executed directly from the Emporium contract's own balance/allowances, with zero verification that the operation's effect is backed by anything the attacker deposited.

### Finding Description
`CircomDataBuilder.formInputForCircom` special-cases the "min" flow: [1](#0-0) 

When `circomData.erc20TokenAddresses.length == 0`, only `emporiumMessage`, `timeStamp`, and `calldataHash` are fed to the circuit — none of the balance-related fields (`amountChanges`, `slippageValues`, `inputNullifiers`, `outCommitments`) are constrained by the proof for this path.

Correspondingly, `Hinkal.transact()` iterates the balance-equation checks only over `circomData.erc20TokenAddresses`: [2](#0-1) 

If that array is empty, the loop body — which enforces `slippageValues`, and the equality `balanceDif == amountChanges[i] + utxoAmount` — never runs at all. `_externalTransact` likewise computes `deltaAmountChanges` over an empty array and calls `runAction` with empty data: [3](#0-2) 

Inside `EmporiumUpgradeable.runAction`, `balancesBefore`/`balancesAfter` are likewise computed over the (empty) `circomData.erc20TokenAddresses`, so the entire post-loop reconciliation (`balanceChange` must be `>= 0`, `handleOut` sweeping proceeds) is skipped: [4](#0-3) 

Meanwhile, the actual arbitrary call still executes unconditionally for every op in `stack.ops`, regardless of whether any token list is tracked: [5](#0-4) 

The only restriction on the stateless branch is blocking the `callHinkalWallet`/`doSendToRelay` selectors; any other `endpoint`/`callData` pair is permitted, including calls that move ERC20 tokens or ETH the Emporium contract currently holds (e.g. residual dust from partial swaps/slippage in other users' external actions, or tokens temporarily routed through the shared Emporium contract as part of concurrent operations) to an attacker-controlled address. Because `circomData.externalActionData` (which embeds the whole `EmporiumStack`/op list) is bound into `calldataHash` and thus into the public input, the *contents* of the malicious op are faithfully what the attacker chose — the proof only attests that the op list is what the attacker committed to, not that its effect is backed by any deposit or balance change the attacker owns. This breaks the balance-conservation equality the protocol otherwise enforces for every other path (`balanceDif == amountChanges[i] + utxoAmount` in `Hinkal.sol` and `balanceChange >= 0` in `EmporiumUpgradeable`): value can leave the shared Emporium pool without being counted against the attacker's own shielded UTXOs.

### Impact Explanation
This is a Critical-impact issue: it allows an unprivileged EOA to move assets (ERC20/ETH balances or allowances held by the shared `Emporium`/`HinkalWallet` infrastructure) that were never authorized by the corresponding depositor's proof or signature, effectively draining pooled protocol/user funds that happen to sit in the Emporium contract at the time of the attack, with no balance check catching the discrepancy.

### Likelihood Explanation
Likelihood depends on the Emporium contract actually holding a spendable balance/allowance at attack time (e.g., transient dust from slippage on multi-hop swaps, or funds mid-flight in another user's multi-op sequence). This is plausible given the shared, non-per-user nature of the Emporium contract and the fact that `handleOut` only sweeps balance *increases* that are explicitly tracked per `erc20TokenAddresses`; any token not included in that list is never swept back to legitimate depositors and is left exposed to this zero-check path.

### Recommendation
Do not allow `formInputEmporiumMin` (empty `erc20TokenAddresses`) to skip balance verification when arbitrary `EmporiumOperation`s are executed. Either: (1) require `erc20TokenAddresses` to include every token touched by any op's `endpoint`, enforced on-chain (e.g., decode/whitelist calldata targets against the declared token list), or (2) always run the balance-before/after check across a protocol-maintained "all tokens the Emporium can hold" set rather than only the caller-supplied list, so any unaccounted asset movement reverts the transaction.

### Proof of Concept
1. Depositor `A`'s prior Emporium interaction leaves residual token `T` balance (e.g., 100 `T`) sitting in the `Emporium` contract due to slippage/dust from an unrelated swap.
2. Attacker `B` submits `Hinkal.transact()` with a trivially valid proof of their own (e.g., zero-value) UTXO, setting `circomData.erc20TokenAddresses = []` and `circomData.externalActionData.externalActionId = HINKAL_EMPORIUM_ACTION_ID`.
3. `circomData.externalActionData.externalActionMetadata` encodes an `EmporiumStack` with `signerAddress = address(0)` and one `EmporiumOperation{ endpoint: address(T), invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.transfer, (B, 100)) }`.
4. `Hinkal.transact()` skips all balance/slippage checks (empty loop) and calls `_externalTransact` → `EmporiumUpgradeable.runAction`, which also skips its balance check (empty `erc20TokenAddresses`) and executes `T.transfer(B, 100)` directly from the Emporium's balance.
5. `B` receives 100 `T` that belonged to the pooled Emporium balance, with no balance-equation revert anywhere in the call path.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-151)
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
```

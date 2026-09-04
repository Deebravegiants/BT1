## Analysis

The Wido report's bug class — an unprivileged, prover-controlled address feeding into privileged execution logic without confirmation — maps onto `EmporiumUpgradeable.runAction` and its `handleOut`/balance-equality logic. However, the strongest reachable analog in this repo is not about validating a Comet-style implementation address; it's about the balance equation only iterating over `circomData.erc20TokenAddresses`, an array chosen entirely by the caller who also supplies arbitrary `EmporiumOperation.endpoint`/`callData`/`value` triples.

### Title
Emporium stateless operations can drain protocol/relay/other-users' ETH and ERC20 balances that are not listed in `erc20TokenAddresses`, bypassing the balance equation - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes arbitrary attacker-chosen `EmporiumOperation`s (`endpoint`, `value`, `callData`) as "Case 2: Stateless Interaction" whenever `stack.signerAddress == address(0)`. In that branch, `verifyWallet` performs **no signature check at all** — it just marks `emporiumMessage` as used and returns. The only balance-equality check afterwards only compares `balancesBefore`/`balancesAfter` for the tokens the caller lists in `circomData.erc20TokenAddresses`, which the caller fully controls as part of their own `CircomData`.

### Finding Description
`transact` → `_externalTransact` → `IExternalActionV2(externalAddress).runAction(circomData, deltaAmountChanges)` dispatches into `EmporiumUpgradeable.runAction` [1](#0-0) . Inside `runAction`, the stack of operations is decoded straight from `circomData.externalActionData.externalActionMetadata` [2](#0-1) .

For the "Stateless Interaction" branch (`op.invokeWallet == false` or `stack.signerAddress == address(0)`), the only restriction is that the callData selector isn't `callHinkalWallet`/`doSendToRelay`; otherwise `op.endpoint.call{value: op.value}(op.callData)` executes with **no destination or fund-source validation** [3](#0-2) . Crucially, `verifyWallet` skips any signature verification entirely when `stack.signerAddress == address(0)` [4](#0-3) , so this path requires no wallet-owner or off-chain signer authorization — only the transact caller's own ZK proof over their own `CircomData`.

The post-call accounting only checks tokens the caller listed:
```solidity
uint256[] memory balancesBefore = getBalancesForArray(circomData.erc20TokenAddresses);
...
uint256[] memory balancesAfter = getBalancesForArray(circomData.erc20TokenAddresses);
for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) { ... }
``` [5](#0-4) 

Since `erc20TokenAddresses` is fully attacker-chosen (it's part of the caller's own `CircomData`, only hashed into `calldataHash`/`signedMessageHash` for integrity, not restricted to a fixed set — see `CircomDataBuilder.getHashedCalldata1`/`formBasicInput`) [6](#0-5) [7](#0-6) , an attacker can simply omit any token they intend to steal (e.g. ETH, or an ERC20 that the Emporium contract holds as protocol/relay-fee residue or leftover balance from other users' in-flight transactions) from the array. The `runAction` balance equality never observes a change in an omitted token, so any amount of that token moved out via the crafted `op.endpoint.call{value: op.value}(op.callData)` is completely uncounted — it breaks the balance equation "change in Emporium balance == sum of off-chain/on-chain UTXO changes" for tokens outside the declared set, because those tokens are silently excluded from both sides of the equation.

The Emporium contract also has an unrestricted `receive() external payable {}` [8](#0-7) , so it can and does accumulate ETH (and ERC20 balances via prior partial fills, dust, or fee residues) between/within transactions, which becomes exposed to this drain.

### Impact Explanation
This is theft of protocol/relay fees and/or temporarily-held user funds (ETH or ERC20 balances sitting in the Emporium contract from other operations) via a call/asset movement the wallet owner or prover for those funds never authorized — matching the "High" impact bucket (temporary freezing/theft of protocol or relay fees, or unauthorized asset movement) and potentially "Critical" if in-flight shielded user funds are present in the contract at call time.

### Likelihood Explanation
Likelihood is moderate-to-high: any unprivileged caller of `Hinkal.transact` can reach `EmporiumUpgradeable.runAction` with `stack.signerAddress == address(0)` and a crafted `EmporiumOperation` list, without needing anyone else's signature, key, or role. The only requirement is producing a valid proof for their own (unrelated) declared `erc20TokenAddresses`/UTXOs — the arbitrary call is fully independent of that proof's economic content since it touches undeclared tokens.

### Recommendation
Enforce that every token balance touched by `op.endpoint.call` operations is included in and validated against `circomData.erc20TokenAddresses` (e.g., snapshot and compare balances for the full set of tokens the contract holds, or restrict `op.endpoint`/`op.callData` targets to an allow-list of known-safe adapters when `signerAddress == address(0)`), and/or forbid arbitrary `value`-bearing low-level calls in the unsigned "Stateless Interaction" path entirely.

### Proof of Concept
1. Attacker deposits/owns at least one shielded UTXO of some token `A` and constructs a valid proof/`CircomData` for a normal Emporium `transact` call, declaring only `erc20TokenAddresses = [A]`.
2. Attacker sets `externalActionData.externalActionMetadata` to an `EmporiumStack` with `signerAddress = address(0)` and one `EmporiumOperation{ endpoint: attackerContract, invokeWallet: false, value: <emporiumEthBalance>, callData: 0x }` (a plain ETH transfer, selector not matching the two blocked ones).
3. `runAction` calls `verifyWallet`, which returns immediately without any signature check (`signerAddress == address(0)`) [9](#0-8) .
4. The loop executes `attackerContract.call{value: emporiumEthBalance}("")`, draining all ETH held by the Emporium contract to the attacker.
5. Because `address(0)` (ETH) is not in the attacker's declared `erc20TokenAddresses = [A]`, the before/after balance loop never inspects ETH, so `runAction` returns normally with a valid `utxoSet` for token `A`, and the stolen ETH is never reconciled against any UTXO output.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L369-369)
```text
    receive() external payable {}
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

**File:** contracts/CircomDataBuilder.sol (L203-209)
```text
        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
```

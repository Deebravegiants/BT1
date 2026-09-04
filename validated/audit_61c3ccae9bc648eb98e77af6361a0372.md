Confirmed: `onlyAllowedRecipient` only checks `msg.sender == Hinkal` (i.e., `runAction` is invoked internally by Hinkal's `_externalTransact`), it does not constrain the *content* of `circomData.externalActionData.externalActionMetadata`, which any unprivileged user fully controls when constructing their own valid ZK proof. This confirms the vulnerability is reachable by any user.

### Title
Arbitrary external call in Emporium's stateless `EmporiumOperation` allows draining any ERC20 token held by the Emporium contract, bypassing the balance-diff check - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction()` decodes an `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` — a field fully controlled by the transaction's author — and, when `stack.signerAddress == address(0)`, executes each `EmporiumOperation` as a raw, unauthenticated `op.endpoint.call{value: op.value}(op.callData)` from the Emporium contract itself. The pre/post balance snapshot used to compute the balance equation only covers `circomData.erc20TokenAddresses` (the tokens declared for *this* transaction), so any token the Emporium contract holds that is *not* in that array is never checked. An attacker can therefore point `op.endpoint` at any ERC20 contract and `op.callData` at `transfer(attacker, balance)` (or `approve`/`transferFrom` if an allowance exists) to scoop out tokens accumulated in Emporium (dust from partial swaps, rounding leftovers, relay-fee remainders, or accidental transfers), exactly analogous to the referenced `settleAuction()` bug where an unchecked `outputToken` parameter let anyone drain unrelated ERC20s from the basket contract.

### Finding Description
In `runAction()` [1](#0-0) , the pre-call balances are only computed for `circomData.erc20TokenAddresses`. `verifyWallet()` performs signature verification only when `stack.signerAddress != address(0)`; when it is `address(0)` it returns immediately without any authentication of `stack.ops` [2](#0-1) . In the main loop, "CASE 2: Stateless Interaction" performs an arbitrary low-level call to `op.endpoint` with `op.callData`, the only restriction being a check that the selector isn't `callHinkalWallet` or `doSendToRelay` [3](#0-2) . Nothing constrains `op.endpoint` to be one of `circomData.erc20TokenAddresses`, and nothing constrains what the call does. Post-call, only balances of `circomData.erc20TokenAddresses` are compared, and `handleOut` only pays out for those declared tokens [4](#0-3) . Although `externalActionMetadata` is included in the ZK proof's `calldataHash` via `CircomDataBuilder.getHashedCalldata1` [5](#0-4) , the circuit only proves that the prover committed to this opaque bytes blob as part of their own balance-consistent transaction — it does not semantically restrict `op.endpoint`/`op.callData` to legitimate DeFi routing calls. Since `runAction` is gated only by `onlyAllowedRecipient`, which merely checks `msg.sender == Hinkal contract` [6](#0-5) , any unprivileged user submitting a normal, self-funded Hinkal transaction through `_externalTransact` can freely author the `EmporiumStack` and target any token contract Emporium happens to hold a balance of, transferring it to themselves. This breaks the balance equation: Emporium's holdings in tokens outside the declared `erc20TokenAddresses` array can change (decrease to zero) with no corresponding entry in `deltaAmountChanges`, `balancesBefore`/`balancesAfter`, or any UTXO output — value leaves the protocol accounting entirely unaccounted for, exactly mirroring the referenced bug where `settleAuction()`'s unchecked `outputTokens` parameter let anyone drain unrelated ERC20 balances from the basket.

### Impact Explanation
High — theft of protocol/relay fees and any incidentally-held ERC20 tokens in the Emporium contract (e.g., dust from partial swaps/rounding, relay fee remainders, or tokens sent by mistake) by an ordinary user with no special privileges, no signer key, and no admin/owner access. If the Emporium accumulates meaningful balances of tokens not part of an in-flight `erc20TokenAddresses` set (a common occurrence with multi-step DeFi routing), this becomes direct theft.

### Likelihood Explanation
High for the attack mechanics (trivial to encode an `EmporiumOperation` with `signerAddress = address(0)` targeting any ERC20's `transfer`), though realized profit depends on Emporium actually holding a residual balance of a token outside the currently declared `erc20TokenAddresses` — a condition that naturally arises from normal swap/relay operation over time (slippage leftovers, fee rounding, partial fills).

### Recommendation
Restrict the stateless-call path so `op.endpoint` can only be one of `circomData.erc20TokenAddresses` (or an explicitly allow-listed router/adapter set), analogous to checking `outputTokens` are part of the basket's tokens in the referenced report. Alternatively, snapshot and diff balances for *all* tokens the Emporium contract could plausibly hold (not just the declared array), or require `signerAddress != address(0)` (i.e., mandatory signature authorization) for any stateless external call that isn't limited to the declared token set.

### Proof of Concept
1. Emporium contract accumulates a balance of `TOKEN_X` (not part of any current transaction's `erc20TokenAddresses`) through normal operation (e.g., rounding dust from a prior swap).
2. Attacker performs an ordinary, self-funded Hinkal deposit/withdraw for an unrelated token `TOKEN_Y`, generating a valid ZK proof for their own UTXOs where `circomData.erc20TokenAddresses = [TOKEN_Y]`.
3. Attacker sets `circomData.externalActionData.externalActionMetadata` to an ABI-encoded `EmporiumStack` with `signerAddress = address(0)` and a single `EmporiumOperation{ endpoint: TOKEN_X, invokeWallet: false, value: 0, callData: abi.encodeWithSelector(IERC20.transfer.selector, attacker, TOKEN_X_balance) }`.
4. `verifyWallet` returns immediately (no signature required) at [7](#0-6) ; the loop executes `TOKEN_X.transfer(attacker, TOKEN_X_balance)` from the Emporium contract at [3](#0-2) .
5. Balance checks only cover `TOKEN_Y`, so the call succeeds and `TOKEN_X` leaves the Emporium contract to the attacker with no accounting impact on the attacker's own legitimate UTXO transaction.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L85-87)
```text
        uint256[] memory balancesBefore = getBalancesForArray(
            circomData.erc20TokenAddresses
        );
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

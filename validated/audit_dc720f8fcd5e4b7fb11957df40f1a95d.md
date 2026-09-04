### Title
Emporium's stateless (non-wallet) external calls execute as the shared Emporium contract identity, letting any Hinkal user hijack and drain funds belonging to another user's Emporium-owned external position - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction` executes user-supplied `EmporiumOperation`s against arbitrary external contracts. When an operation is *stateless* (`invokeWallet == false` or `signerAddress == address(0)`), the low-level call is made directly from `EmporiumUpgradeable` itself: `op.endpoint.call{value: op.value}(op.callData)` [1](#0-0) . `EmporiumUpgradeable` is a single shared singleton contract used by every Hinkal user, so any external protocol position/order/deposit created this way is owned, from the external protocol's perspective, by the Emporium contract address itself - not by the individual depositor. Any other Hinkal user can later submit their own proof with a stateless `EmporiumOperation` targeting that same external protocol's withdraw/cancel/claim function for someone else's position id; the call succeeds because `msg.sender` is still Emporium. The resulting balance increase on Emporium is then swept entirely to the caller via `handleOut`, since the balance-delta accounting has no notion of "whose position" produced the funds.

### Finding Description
`EmporiumUpgradeable.runAction` computes `balancesBefore`/`balancesAfter` for the declared tokens, executes the caller-supplied ops, and then attributes any positive balance change to the current caller: [2](#0-1) 

`handleOut` unconditionally forwards any positive balance change on the tracked token to `msg.sender` and mints them a UTXO for it, with zero checks that this balance change is actually attributable to *this* caller's own action rather than to residual state Emporium held from a *different* user's earlier interaction: [3](#0-2) 

The `op.endpoint` / `op.callData` values are fully attacker-chosen; they are only bound into `calldataHash`, which is merely an integrity check that the circuit's public inputs match the transaction's own `circomData` - it does not constrain which external contract/function is called nor tie the call to any specific pre-existing position/commitment: [4](#0-3) [5](#0-4) 

Contrast this with the "Stateful" (CASE 1) path, where the external call is routed through the user's own per-signer `HinkalWallet` (an EIP-1271 wallet contract whose `onlyEmporium` modifier still lets Emporium invoke it, but the wallet address itself - and hence external-protocol ownership - is scoped per signer): [6](#0-5) 

In the stateless path there is no such per-user scoping - the identity used against the external protocol is always the shared `EmporiumUpgradeable` address. This is structurally the same root cause as the referenced RubiconRouter finding: a shared intermediary contract becomes the recorded "owner" of an externally-tracked value-bearing object (offer/position/deposit) with no mechanism restricting who may later act on that ownership. Here it is strictly worse than the original report: instead of merely locking the depositor's funds, it allows an *unrelated* third party to trigger the withdrawal/cancellation and redirect the proceeds to themselves.

### Impact Explanation
Any user who can discover or guess the calldata needed to withdraw/cancel/claim a previously-created Emporium-owned external position (e.g. an order-book offer, a lending withdrawal, an LP unstake) can craft a new, entirely-valid Hinkal proof (spending only their own UTXOs, with `deltaAmountChanges[i] == 0` for the targeted token) whose `EmporiumOperation` calls that withdrawal function. The proceeds land on Emporium's balance and are swept to the attacker via `handleOut`. This is direct theft of another user's protocol-held funds - a Critical-severity impact (unauthorized asset movement never authorized by the position's original prover/depositor).

### Likelihood Explanation
Exploitability depends on the attacker knowing the external protocol's call interface and the relevant object/position identifier used in a prior stateless Emporium interaction (often discoverable from on-chain calldata/events of the earlier transaction, or via IDs incrementing predictably). Given that stateless ops are a documented, first-class code path (explicitly named "CASE 2: Stateless Interaction" in the code) intended for integrations that don't require a persistent per-user wallet, likelihood of this pattern being used with any protocol having withdrawable/cancellable state is realistic.

### Recommendation
- Disallow stateless (`signerAddress == address(0)`) Emporium operations for any external protocol interaction that creates a persistent, later-actionable position/order/deposit whose ownership is recorded as the caller (`msg.sender == Emporium`) address; require such interactions go through the per-signer `HinkalWallet` (CASE 1) so that only the original depositor's wallet is the recognized owner.
- Alternatively, bind stateless-created positions to depositor identity within Emporium itself (e.g., record `positionOwner[externalContract][positionId] = signerHash` at creation) and require any Emporium-triggered withdrawal to go through the recorded owner check before crediting `handleOut`'s balance-based payout to the current caller.
- At minimum, ensure `handleOut`'s balance-delta accounting cannot attribute balance increases to a caller who did not initiate the specific action (e.g., require an explicit allowlist of stateless op selectors per external target, excluding withdraw/cancel/claim-type functions unless routed via the wallet).

### Proof of Concept
1. User A calls `Hinkal.transact` with a valid proof and an `EmporiumOperation` (stateless, `signerAddress == address(0)`) that calls `externalMarket.createOffer(...)`. `EmporiumUpgradeable` is recorded by `externalMarket` as the offer's owner, and User A's shielded tokens flow from Emporium to `externalMarket`.
2. User B (attacker), independently, calls `Hinkal.transact` with their own valid proof (spending only their own UTXOs, `deltaAmountChanges[i] == 0` for the offer's token) and a stateless `EmporiumOperation` calling `externalMarket.cancelOffer(offerId)` for User A's offer id.
3. `externalMarket` accepts the cancel since `msg.sender == Emporium == offer.owner`; the offer's locked tokens are returned to `EmporiumUpgradeable`'s balance.
4. `runAction`'s balance-delta logic in `EmporiumUpgradeable.sol` (lines 122-151) sees `balanceChange > 0` for that token (since User B's own `deltaAmountChanges[i]` is 0), and `handleOut` (lines 162-184) transfers the full amount to User B (`msg.sender`) and mints User B a UTXO for it - stealing User A's funds.

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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

**File:** contracts/CircomDataBuilder.sol (L10-18)
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
```

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L28-34)
```text
    function callHinkalWallet(
        address endpoint,
        bytes calldata data,
        uint value
    ) external onlyEmporium returns (bool success, bytes memory err) {
        (success, err) = endpoint.call{value: value}(data);
    }
```

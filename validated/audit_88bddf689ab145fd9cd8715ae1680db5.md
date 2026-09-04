### Title
Arbitrary `endpoint.call` in `EmporiumUpgradeable.runAction` lets an unprivileged user drain ERC20 balances the Emporium contract holds outside the attacker's declared `erc20TokenAddresses` list - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` decodes a fully attacker-controlled `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and, in the "stateless interaction" branch, executes `op.endpoint.call{value: op.value}(op.callData)` directly in the Emporium contract's own context, with no restriction on `endpoint`/`callData` and no signature requirement when `stack.signerAddress == address(0)`. This is the same "unsafe arbitrary call from a shared, non-isolated contract" pattern flagged in the external report for `OpportunityAdapter`. Because the post-call balance reconciliation in `runAction` only nets balances for the ERC20 tokens the caller lists in `circomData.erc20TokenAddresses`, an attacker can move any *other* ERC20 token the shared Emporium contract happens to hold (e.g. dust left over from prior swaps/fees, or balances parked by another user's multi-step Emporium interaction) to themselves via a crafted `EmporiumOperation`, entirely unaccounted for by the equality check.

### Finding Description
`EmporiumUpgradeable.runAction` [1](#0-0)  loops over `stack.ops` and, when `op.invokeWallet` is false (or `stack.signerAddress == address(0)`), calls:

```solidity
(success, err) = op.endpoint.call{value: op.value}(op.callData);
``` [2](#0-1) 

`verifyWallet` only checks a signature when `stack.signerAddress != address(0)`; if it's the zero address, verification is skipped entirely [3](#0-2) . So a user can submit a valid zk-proof for their own UTXOs/nullifiers while attaching an `EmporiumStack` whose `ops` are completely self-authored and unchecked by any external signer.

`runAction` reconciles balance changes only for the tokens listed in `circomData.erc20TokenAddresses`, comparing `balancesBefore`/`balancesAfter` for exactly that array [4](#0-3) [5](#0-4) . Any ERC20 token not included in that attacker-chosen array is never checked - `op.endpoint.call` can target that token's `transfer`/`transferFrom` function and move it out of the shared `EmporiumUpgradeable` contract's balance with zero effect on the equality guard.

Because `EmporiumUpgradeable` is a single shared, non-isolated contract (unlike `HinkalWallet`, which is deployed per-user and is exactly the factory/Create2 isolation pattern the external report recommends as remediation for this bug class [6](#0-5) ), any ERC20 balance it holds - from prior partially-completed multi-op flows, swept dust, rounding remainders in `handleOut`, or fee remnants - is shared attack surface for every user of the protocol, not just the one who caused the balance to exist.

### Impact Explanation
This breaks the balance/equality invariant `runAction` is meant to enforce: total ERC20 movement caused by the arbitrary calls must be captured by `balancesBefore`/`balancesAfter` for `circomData.erc20TokenAddresses`. An attacker can choose an `erc20TokenAddresses` array that omits the token they intend to steal, use a legitimate/self-owned UTXO for the tokens actually declared (satisfying the circuit and nullifier checks), and add an `EmporiumOperation` that calls `transfer`/`transferFrom` on an undeclared ERC20 held by the Emporium contract, sending it to themselves. This is theft of protocol/relay/user funds held by a shared, non-isolated contract - a High/Critical impact depending on how much value the Emporium contract accumulates over time.

### Likelihood Explanation
Likelihood depends on the Emporium contract actually holding un-swept ERC20 balances belonging to other flows (dust, partially completed stateful sequences, fee remainders in `handleOut`'s `balanceChange` rounding, or leftover funds from any multi-op sequence that isn't fully withdrawn in the same transaction). Since nothing in `runAction` restricts `op.endpoint`/`op.callData`, and `stack.signerAddress == address(0)` requires no external authorization, exploitation requires only that the attacker submit a normal, self-authored proof/transaction - no privileged role, admin key, or victim cooperation is needed.

### Recommendation
- Restrict the "stateless interaction" call target/selector so it cannot invoke ERC20 `transfer`/`transferFrom`/`approve` (or any state-mutating call) on tokens outside `circomData.erc20TokenAddresses`, or better, disallow calling ERC20 token contracts directly from this branch entirely.
- Ensure the post-call reconciliation sweeps and enforces non-negative balance deltas for every token the `ops` array can possibly touch, not just the caller-declared `erc20TokenAddresses`, e.g. by deriving the token list from statically decoding `op.callData` targets, or by never letting the contract hold ERC20 balances across transactions (sweep to zero at the end of every `runAction`).
- Consider requiring `stack.signerAddress` (and hence a signature) for any op that isn't provably scoped to the caller's own declared tokens/amounts.

### Proof of Concept
1. Assume `EmporiumUpgradeable` currently holds `100 USDC` of undeclared dust (left over from a previous swap/fee rounding via `handleOut`, or a partially completed multi-op flow by another user).
2. Attacker builds a normal Hinkal `transact` call with valid nullifiers/proof for their own UTXOs, setting `circomData.erc20TokenAddresses = [DAI]` (a token they legitimately hold zero delta for) and `externalActionData.externalAddress = EmporiumUpgradeable`.
3. In `externalActionData.externalActionMetadata`, attacker encodes an `EmporiumStack` with `signerAddress = address(0)` (skips `verifyWallet` signature check) and one `EmporiumOperation`: `endpoint = USDC`, `invokeWallet = false`, `callData = abi.encodeWithSelector(IERC20.transfer.selector, attacker, 100e6)`.
4. `runAction` executes `op.endpoint.call(op.callData)` from the Emporium contract's own context, transferring the 100 USDC to the attacker. Since USDC isn't in `circomData.erc20TokenAddresses = [DAI]`, `balancesBefore`/`balancesAfter` never observe this movement, so `BalanceChangeShouldBePositive` is never triggered and the theft passes unnoticed by the equality check [7](#0-6) .

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-118)
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
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-145)
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

**File:** contracts/external-actions/emporium/HinkalWallet.sol (L10-19)
```text
contract HinkalWallet is Transferer, IHinkalWallet {
    address public immutable emporium;

    event EthReceivedOnWallet(address indexed sender, uint256 amount);

    error NotAllowedToCallWallet();

    constructor(address _emporium) {
        emporium = _emporium;
    }
```

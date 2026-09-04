### Title
Unprivileged EOA can force `Emporium` to grant itself an infinite, persistent ERC20 approval on any token the contract holds, via an unconstrained arbitrary-endpoint call in the "Stateless Interaction" branch of `runAction` - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction` executes a stack of attacker-supplied `EmporiumOperation`s. When `stack.signerAddress == address(0)` ("Stateless Interaction"), `verifyWallet` performs no signature check at all [1](#0-0) , and the loop executes `op.endpoint.call{value: op.value}(op.callData)` where `op.endpoint` and `op.callData` are fully attacker-controlled, with only two selectors blacklisted [2](#0-1) . This is the same bug class as the LI.FI `AnyswapFacet` report: the contract makes an arbitrary, attacker-directed external call that can be used to grant an infinite ERC20 `approve()` to an attacker-controlled address for any token, from `address(this)` (the `Emporium` contract).

### Finding Description
`EmporiumStack`, decoded from `circomData.externalActionData.externalActionMetadata`, is passed by the caller and only its post-execution net balance effect is checked, not the semantics of each call [3](#0-2) . Because `approve()` does not move any ERC20 balance, an attacker can include an operation with:
- `op.endpoint` = any ERC20 token address (not necessarily one listed in `circomData.erc20TokenAddresses`)
- `op.callData` = `approve(attacker, type(uint256).max)`
- `op.invokeWallet = false`, `stack.signerAddress = address(0)`

This call is made with `msg.sender == address(this)` (Emporium), so it grants the attacker unlimited spending rights on any ERC20 balance the `Emporium` contract holds — now or in the future. The end-of-function balance check only compares `balancesAfter[i]` vs `balancesBefore[i]` for the tokens listed in `circomData.erc20TokenAddresses` [4](#0-3) , and even for a listed token, an `approve()` call causes no balance delta, so it passes trivially. The approval persists after the transaction completes, unlike the transient in-call funds; any token balance that later ends up in `Emporium` (leftover dust, un-swept relay fees, or a subsequent user's tokens transferred in via `Hinkal._externalTransact` prior to their own `runAction` executing) becomes stealable by calling `transferFrom` in a separate follow-up transaction.

This exactly mirrors the referenced `AnyswapFacet`/`LibAsset.approveERC20` root cause: an externally-facing function grants (or here, allows granting) unlimited ERC20 approval to an address that ultimately comes from attacker calldata, without any allow-listing of the approved spender. In `LifiExternalAction.callRouter` the analogous approval target `router` is a fixed `immutable` address set at deploy time [5](#0-4) , so that path is not exploitable this way; but `Emporium`'s stateless branch has no such restriction on `op.endpoint`.

The equality broken is the value-accounting invariant the design tries to enforce ("total change of emporium balance == what was moved in during the tx"), comment at [6](#0-5) : the check only covers *balance* changes within the current call, but an infinite `approve()` is a state change that moves value outside this equality — the funds only leave later, in a separate transaction, once other funds have accrued in the contract.

### Impact Explanation
This is a "value moved by Hinkal/an external action but not counted in the balance equation" analog. Any ERC20 tokens that land in the `Emporium` contract at any future point (protocol/relay fee remnants, rounding dust from swaps, tokens deposited for another user's in-flight multi-op stack before their `runAction` completes) can be stolen by any attacker who has previously planted such an approval, with no signature, no proof-of-ownership of those funds, and no admin/relayer trust assumption required. This matches High severity per the taxonomy ("theft or permanent freezing of protocol/relay fees, temporary freezing of user funds, executing calls or moving assets a wallet owner or prover never authorised") and can rise to Critical if in-flight shielded user funds transiently held by `Emporium` (per `Hinkal._externalTransact`, which transfers funds to the external action address *before* invoking `runAction`) are drained mid-flow by a racing attacker.

### Likelihood Explanation
Any unprivileged EOA can trigger this by submitting a normal, valid Hinkal transaction that routes through `Emporium` as the `externalActionData.externalAddress` with a crafted `externalActionMetadata`. No signature is required in the stateless branch (`signerAddress == address(0)` is a legitimate, supported mode, not an edge case), and no code inspects `op.endpoint`/`op.callData` beyond two blocked selectors. The only prerequisite is that `Emporium` holds (or will hold) an ERC20 balance at the time of exploitation, which the protocol's own design acknowledges can happen (leftover dust/fees), consistent with the original report's finding that diamond/proxy contracts routinely accumulate residual balances.

### Recommendation
- Restrict the "Stateless Interaction" branch to disallow calling arbitrary token contracts, or maintain an explicit allow-list of `op.endpoint` addresses (e.g., only pre-approved DEX routers), analogous to the fix pattern recommended for `AnyswapFacet`.
- Alternatively/additionally, block state-changing calls to any address in `circomData.erc20TokenAddresses` (or any ERC20-like contract) from the stateless branch, or specifically blacklist the `approve`/`increaseAllowance`/`permit`-style selectors in addition to `callHinkalWallet`/`doSendToRelay`.
- Ensure `Emporium` never carries a standing ERC20 balance between transactions (sweep-to-zero at the end of `runAction`), so a rogue historical approval cannot be exploited even if granted.

### Proof of Concept
1. Attacker holds a valid Hinkal UTXO/proof enabling a call to `runAction` on `Emporium` via `Hinkal._externalTransact` (any legitimate deposit/withdraw circuit works; `externalActionData.externalAddress` = `Emporium`).
2. Attacker crafts `circomData.externalActionData.externalActionMetadata` to decode into an `EmporiumStack` with `signerAddress = address(0)` and one `EmporiumOperation`:
   - `endpoint = <any ERC20 token, e.g., USDC>`
   - `callData = abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)`
   - `invokeWallet = false`, `value = 0`
3. `verifyWallet` short-circuits with no signature check [1](#0-0) ; the loop executes `USDC.call(approve(attacker, MAX))` from `Emporium`, succeeding trivially [2](#0-1) .
4. Since `USDC` need not even be in `circomData.erc20TokenAddresses`, and even if it is, `approve` causes zero balance delta, the post-call `balanceChange < 0` check never triggers [7](#0-6) ; the transaction completes successfully, minting the attacker a persistent `MAX` allowance on `Emporium`'s USDC.
5. At any later time, whenever `Emporium` holds a nonzero USDC balance (dust, fees, or another user's in-flight deposit), the attacker calls `USDC.transferFrom(Emporium, attacker, balance)` directly, draining those funds.

Note: I was unable to fully verify within the available tool budget whether `calldataHash`/the circuit's public-input binding in `contracts/CircomDataBuilder.sol` and `circuits/MainEVMCircuit.circom` places any additional constraint that would prevent an attacker from freely choosing `externalActionMetadata` contents (as opposed to merely committing to a hash of it that the attacker themselves computes as the prover). Given the prover is the attacker's own key and the operation requires no third-party signature, this is not expected to block the attack, but this remains an assumption not fully confirmed against the circuit constraints.

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L122-144)
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L314-316)
```text
        if (stack.signerAddress == address(0)) {
            return;
        }
```

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L6-18)
```text
contract LifiExternalAction is ExternalActionSwap {
    constructor(
        address _hinkalHelper,
        address _wrapper,
        address _router,
        address[] memory _allowedRecipients
    )
        ExternalActionSwap(_hinkalHelper, _wrapper, _router, _allowedRecipients)
    {}

    function callRouter(
        address inputToken,
        uint256 inputAmount,
```

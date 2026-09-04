### Title
Unauthorized arbitrary calls from `EmporiumUpgradeable` allow planting a persistent `approve()` backdoor on tokens outside the balance-checked set - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.runAction()` executes user-supplied `EmporiumOperation[]` calls with the Emporium contract itself as `msg.sender` whenever `stack.signerAddress == address(0)` ("stateless interaction", CASE 2). In that mode `verifyWallet()` performs **no signature check at all** and simply marks the message used. Any unprivileged EOA that can produce one valid Hinkal ZK proof (even for a trivial/self-created shielded balance) can therefore make the Emporium contract call an arbitrary `endpoint` with arbitrary `callData`, on a token that is never included in `circomData.erc20TokenAddresses` and is thus never covered by the post-call balance-equality check.

### Finding Description
`runAction()` decodes an `EmporiumStack` from `circomData.externalActionData.externalActionMetadata` and, for CASE 2 ops, executes: [1](#0-0) 

The only restriction is that the call's function selector cannot be `callHinkalWallet`/`doSendToRelay`; any other target and calldata is permitted. `verifyWallet()` is supposed to gate this, but when `stack.signerAddress == address(0)` it returns immediately without any signature verification: [2](#0-1) 

The only invariant enforced afterward is a per-token balance equation over `circomData.erc20TokenAddresses` (the array the caller itself declares): [3](#0-2) 

Because the attacker fully controls `circomData.erc20TokenAddresses`, they can simply omit any token they don't want balance-checked, and target an `op` at that token's `approve(address,uint256)` function. Since the call is executed with `msg.sender == address(Emporium)`, it grants `IERC20(anyToken).approve(attacker, type(uint256).max)` from the Emporium contract, an address that later accumulates token balances belonging to other users mid-transaction (e.g. amounts moved in by `_externalTransact` before `runAction` and by residual fee/rounding dust), and holds them across the lifetime of the contract: [4](#0-3) 

`onlyAllowedRecipient` only checks that the caller is the registered Hinkal entrypoint, not that the wallet owner authorized this particular set of `ops`: [5](#0-4) 

The `calldataHash`/proof machinery only proves that the submitted `circomData` (including the malicious `externalActionMetadata`) matches what the *attacker's own* proof was generated for; it never proves that any *other* party authorized these ops (`CircomDataBuilder.getHashedCalldata`/`performHinkalChecks`): [6](#0-5) 

So the equality that breaks is: value/authority moved by the Emporium contract (a standing `approve()` on an arbitrary ERC20) is never reflected in, or constrained by, the balance-equality check that is supposed to bound every asset the contract touches during `runAction`.

### Impact Explanation
An attacker who has deposited/withdrawn even a trivial (e.g. 1 wei) shielded amount can obtain a valid proof and use it purely as a ticket to make the Emporium contract execute an `approve()` (or any other state-mutating call) as itself, on any ERC20 token, without ever declaring that token in the balance-checked array. Any token balance the Emporium contract subsequently holds (deposits-in-flight from other users' concurrent/future transactions, relay-fee dust, rounding remainders) becomes drainable by the attacker via a later `transferFrom`. This is theft of protocol/relay funds that the attacker never had a claim to and never authorized by any legitimate signer, matching the High-impact category ("theft ... of protocol/relay fees", "executing calls or moving assets ... a prover never authorised" with respect to other users' funds later held by Emporium).

### Likelihood Explanation
Reachable by any unprivileged EOA with no special role: only a syntactically valid Hinkal proof (of the attacker's own shielded UTXO, however small) plus a crafted `EmporiumStack` with `signerAddress = address(0)` is required. `verifyWallet` intentionally skips signature checks for this branch, which is meant for stateless self-serve ops but places no restriction on which token/endpoint can be touched, and imposes no scoping between `ops` targets and `circomData.erc20TokenAddresses`.

### Recommendation
For CASE 2 "stateless" ops, restrict `op.endpoint` to only the tokens declared in `circomData.erc20TokenAddresses` (or to a fixed allow-list of router/endpoint addresses), and/or forbid arbitrary calldata to `approve`/`increaseAllowance`-style selectors on any ERC20 from the Emporium's own context. Alternatively, require `stack.signerAddress != address(0)` (i.e., mandatory owner signature) for any op whose target is not itself one of the declared, balance-checked tokens, so that granting allowances or making arbitrary calls "as Emporium" is always tied to an explicit, provable authorization.

### Proof of Concept
1. Attacker deposits a trivial amount (e.g. 1 wei of any token) into the shielded pool via `prooflessDeposit`.
2. Attacker generates a valid Hinkal proof to spend this UTXO with `externalActionData.externalAddress = Emporium` and `externalActionMetadata` encoding an `EmporiumStack` with `signerAddress = address(0)` and a single op: `{endpoint: victimToken, invokeWallet: false, value: 0, callData: abi.encodeCall(IERC20.approve, (attacker, type(uint256).max))}`. `victimToken` is deliberately NOT included in `circomData.erc20TokenAddresses`.
3. Calls `Hinkal.transact()`. `performHinkalChecks` passes (the proof matches the attacker's own submitted `circomData`). `_externalTransact` invokes `EmporiumUpgradeable.runAction`.
4. `verifyWallet` returns immediately (`stack.signerAddress == address(0)`), no signature required.
5. CASE 2 branch executes `victimToken.call(approve(attacker, max))` with `msg.sender = Emporium`. The balance-equality loop never examines `victimToken` since it's absent from `circomData.erc20TokenAddresses`, so nothing reverts.
6. Whenever Emporium later holds any balance of `victimToken` (from other users' withdrawals in flight, dust, etc.), attacker calls `victimToken.transferFrom(Emporium, attacker, amount)` to steal it.

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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

### Title
Cross-token balance aliasing lets a malicious "double-entry" token break Hinkal.transact's `balanceDif == amountChanges[i] + utxoAmount` invariant, minting shielded UTXOs unbacked by real assets - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact` verifies solvency per-token by independently comparing each `erc20TokenAddresses[i]` entry's `balanceOf()` delta against the UTXOs it minted for that same address. Because the check is done index-by-index using raw `balanceOf()` snapshots (`getBalancesForArray`), and nothing anywhere on-chain (or in the circuit) verifies that two different addresses in `erc20TokenAddresses` represent economically independent assets, an attacker can list a second, attacker-deployed token address that mirrors/aliases the real balance of another listed token. This makes the per-token check pass for both entries while only one real transfer of value actually entered the vault.

### Finding Description
The broken equality is:
`sum(real value that entered Hinkal in this tx) == sum(circomData.amountChanges[i]) + sum(minted on-chain UTXO amounts)`

`Hinkal.transact` snapshots balances before/after the external action and checks this per index `i` independently: [1](#0-0) [2](#0-1) 

`getBalancesForArray`/`getERC20OrETHBalance` simply call `balanceOf(address(this))` on each listed token address: [3](#0-2) 

The only guard restricting `erc20TokenAddresses` entries is a pairwise numeric-inequality check in the circuit, which only forbids the literal same address from appearing twice — it says nothing about whether two different addresses represent the same or a related real balance: [4](#0-3) 

`DepositOnChainUtxosExternalAction.runAction` pulls tokens from the user per index and mints an on-chain UTXO whose amount is fully attacker-chosen via `externalActionMetadata` (`utxoAmounts`), with no cross-index correlation check: [5](#0-4) 

Exploit: attacker deploys token `A` (a real, normal ERC20) and token `B`, a "shadow" contract whose `balanceOf(vault)` is defined as a function of `A`'s real balance for the vault (e.g. `B.balanceOf(x) = 2 * A.balanceOf(x)`), while `B.transferFrom(...)` either is a no-op or, worse, is wired as an alias/proxy that shares `A`'s real storage so that redemptions of `B` later actually move real `A` tokens. Attacker calls `Hinkal.transact` (self-generating a valid proof for their own action, `externalActionId` pointing at `DepositOnChainUtxosExternalAction`) with `erc20TokenAddresses = [A, B]`, `utxoAmounts = [[X], [2X]]`.
- `oldBalances = [balA, 2*balA]` (both read before the run).
- `runAction` transfers real `X` of `A` from user to Hinkal for index 0, does no real transfer of value for index 1 (only a fake/no-real-effect `transferFrom` on `B`).
- `newBalances = [balA+X, 2*(balA+X)]` because `B`'s view mirrors `A`.
- `balanceDif[0] = X`, matches `utxoAmount[0] = X` → passes.
- `balanceDif[1] = 2X`, matches attacker-chosen `utxoAmount[1] = 2X` → passes.

Both per-index `require`s in `Hinkal.transact` are satisfied even though only `X` of real value entered the vault, while `3X` worth of on-chain UTXOs (`X` for `A` + `2X` for `B`) were minted and inserted into the merkle tree via `insertCommitments`. None of `performHinkalChecks`, `dimensionsCheck`, `checkOnchainCreation`, `insertNullifiers`, or the circuit's `distinctErc20AddressChecks`/`inTotal + amountChanges === outTotal` constraints detect this, because all of them operate strictly per declared token index and never verify that distinct addresses are economically unrelated assets.

Note: the question's framing that this must be "routed through HinkalWrapper's fee settlement first" does not correspond to a real code path — `HinkalWrapper` only wraps `prooflessDeposit` (a separate, proof-less flow) and never calls `Hinkal.transact` or interacts with `DepositOnChainUtxosExternalAction`: [6](#0-5) 
The attack does not require or benefit from that hop; it is fully reachable by calling `Hinkal.transact` directly.

### Impact Explanation
The attacker mints shielded on-chain UTXOs (`2X` for token `B`) that are not backed by any real value deposited into the vault, while a genuinely-backed `X` UTXO for token `A` is also created. If `B`'s redemption path is later wired (or simply attacker-controlled) to draw down real reserves (e.g., shared storage with `A`, or `B` simply representing a claim later exchanged inside the shielded pool against `A`/other real tokens through internal transfers), the protocol becomes insolvent by the unbacked `2X`. This is a Critical-severity "minting shielded value without backing" finding, and it is repeatable per transaction/per malicious token deployed by the attacker.

### Likelihood Explanation
The attacker needs no privileged role: they can deploy an arbitrary ERC20-like contract, deposit their own funds, and generate their own valid proof for a `DepositOnChainUtxosExternalAction`-routed `transact` call (assuming this external action is registered, which is a normal operational state, not a privilege the attacker needs). The only precondition is that Hinkal accepts arbitrary, unwhitelisted `erc20TokenAddresses` (confirmed — no on-chain whitelist exists in `dimensionsCheck`/`performHinkalChecks`), which is the case here. Cost is limited to gas and deploying one malicious token contract; the attack is fully repeatable.

### Recommendation
Do not trust per-index `balanceOf()` deltas as proof of asset-specific solvency when multiple token addresses are supplied in one transaction. Either (a) whitelist tokens allowed in `erc20TokenAddresses`, or (b) compute a single aggregate real-value check across the whole array rather than per-index in isolation is insufficient too since aliasing still corrupts aggregate sums — the real fix is to restrict `erc20TokenAddresses` to a vetted allow-list of tokens (preventing attacker-deployed "mirror" contracts from being listed at all), and/or require that balance snapshots be taken and diffed strictly around the specific token's own explicit transfer call rather than a global before/after over the whole batch.

### Proof of Concept
Foundry test plan:
1. Deploy real token `A` (standard ERC20, mint balance to test user).
2. Deploy malicious token `B` whose `balanceOf(addr)` returns `2 * A.balanceOf(addr)`, and whose `transferFrom` either no-ops or forwards to a shared/aliased storage scheme so it does not add new real reserve.
3. Register `DepositOnChainUtxosExternalAction` as external action id `N` in `Hinkal` (owner setup, non-privileged for attacker in exploit).
4. Attacker constructs `circomData` with `erc20TokenAddresses = [A, B]`, `amountChanges = [0,0]`, `onChainCreation = [true,true]`, `externalActionData.externalActionMetadata = abi.encode([[X],[2X]])`, generates a valid proof for this transaction.
5. Call `Hinkal.transact(...)`.
6. Assert: `A.balanceOf(hinkal) - balA_before == X` (real value received), while merkle tree/UTXO commitments record `X` for `A` and `2X` for `B`, i.e., total credited value `3X != X` real value received — invariant `sum(amountChanges) + sum(minted UTXO amounts) == real value entering vault` is violated (`3X != X`), confirming unbacked minting.

### Citations

**File:** contracts/Hinkal.sol (L78-90)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );
```

**File:** contracts/Hinkal.sol (L136-146)
```text
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
```

**File:** contracts/Transferer.sol (L149-176)
```text
    function getERC20OrETHBalance(
        address _erc20TokenAddress
    ) internal view returns (uint256) {
        if (_erc20TokenAddress == address(0)) {
            return address(this).balance;
        } else {
            IERC20 outToken = IERC20(_erc20TokenAddress);
            return outToken.balanceOf(address(this));
        }
    }

    function getBalancesForArrayMemory(
        address[] memory erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }

    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }
```

**File:** circuits/MainEVMCircuit.circom (L171-182)
```text
  component distinctErc20AddressChecks[tokenCount * (tokenCount-1)/2];
  var index = 0;
  for (var i =0; i< tokenCount-1;i++){
    for (var j = i+1; j< tokenCount; j++)
    {
      distinctErc20AddressChecks[index] = IsEqual();
      distinctErc20AddressChecks[index].in[0] <== erc20TokenAddresses[i];
      distinctErc20AddressChecks[index].in[1] <== erc20TokenAddresses[j];
      distinctErc20AddressChecks[index].out === 0;
      index++;
    }
  }
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-86)
```text
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
        }

        emit BlockedUtxosCreated();
    }
```

**File:** contracts/HinkalWrapper.sol (L28-47)
```text
    function prooflessDeposit(
        address[] calldata erc20Addresses,
        uint256[] calldata amounts,
        StealthAddressStructure[] calldata stealthAddressStructures,
        bytes[] calldata onChainEncryptedOutputs,
        bool createBlockedUtxos,
        ProoflessFeeStructure calldata feeStructure,
        string calldata orderId
    ) external payable {
        uint256 ethForHinkal = _settleFee(feeStructure);
        _pullAndApproveDepositTokens(erc20Addresses, amounts);
        IHinkal(hinkal).prooflessDeposit{value: ethForHinkal}(
            erc20Addresses,
            amounts,
            stealthAddressStructures,
            onChainEncryptedOutputs,
            createBlockedUtxos,
            orderId
        );
    }
```

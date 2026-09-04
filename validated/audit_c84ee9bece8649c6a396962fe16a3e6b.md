### Title
Cross-index balance-alias token lets a single real deposit back two `onChainCreation` UTXO mints in `DepositOnChainUtxosExternalAction` - (File: contracts/Hinkal.sol :: transact)

### Summary
`Hinkal.transact` snapshots `balanceOf()` for the entire `circomData.erc20TokenAddresses` array once before and once after the whole external action, then validates each index independently with `balanceDif == (onChainCreation? 0 : amountChanges[i]) + utxoAmount`. Because token addresses are fully attacker-supplied and only checked for pairwise value-inequality in the circuit, an attacker can include a second, self-deployed "alias" token whose `balanceOf()` mirrors a real token's balance at the vault while its `transferFrom` is a no-op, letting one real deposit satisfy the equality check twice and mint an unbacked on-chain UTXO.

### Finding Description
The invariant that must hold is: *real tokens entering the vault for a given `erc20TokenAddresses[i]` == `amountChanges[i]` (or 0 if `onChainCreation[i]`) + sum of on-chain UTXO amounts minted under `erc20TokenAddresses[i]`*.

`Hinkal.transact` computes this with a single pair of snapshots for the *entire* array, not per index: [1](#0-0) 
and then checks the per-index equality using those global snapshots: [2](#0-1) 

The circuit's only defense on token-address distinctness is a pure address-value inequality check, which says nothing about whether two addresses actually represent independent economic balances: [3](#0-2) 

`DepositOnChainUtxosExternalAction.runAction` couples, per index, the ERC20 amount pulled from the user to the UTXO amount minted for that same index — but it processes multiple indices sequentially inside one call, and the per-index token address is entirely attacker-controlled and unvalidated beyond being distinct as a raw address value: [4](#0-3) 

Exploit: the attacker deploys two contracts:
- `TokenA` = the real token they will legitimately deposit (e.g. a wrapped/real ERC20 the vault already holds balances of, or simply their own genuine token).
- `TokenB` = a "double-entry" alias contract whose `balanceOf(hinkal)` forwards to `TokenA.balanceOf(hinkal)` (or to whichever real token’s balance they want to mirror), but whose `transferFrom` is a no-op that returns `true` without moving any value.

They call `Hinkal.transact` with `erc20TokenAddresses = [TokenA, TokenB]`, both `onChainCreation[i] = true`, `amountChanges = [0, 0]`, and `externalActionData` targeting `DepositOnChainUtxosExternalAction` with `utxoAmounts = [[X], [X]]`. Inside `runAction`:
- index 0 (`TokenA`): a real transfer of `X` tokens from the attacker to Hinkal occurs, and a UTXO of amount `X` under `TokenA` is minted.
- index 1 (`TokenB`): `transferFrom` is a no-op (no real value moves), but a UTXO of amount `X` under `TokenB` is minted anyway.

Back in `Hinkal.transact`, `oldBalances`/`newBalances` are taken once for the *whole* array, before and after the entire `runAction` call. Because `TokenB.balanceOf(hinkal)` mirrors `TokenA`'s real balance, and `TokenA`'s real balance rose by `X` during the same call (from index 0's real transfer), `newBalances[1] - oldBalances[1]` also equals `X` — even though nothing was actually deposited for index 1. The check for index 1, `balanceDif == 0 (onChainCreation) + utxoAmount(X)`, passes (`X == X`), so the vault mints a second, fully unbacked on-chain UTXO for `X` using only one real deposit of `X`.

This works because `getBalancesForArray`/`getERC20OrETHBalance` blindly trusts `balanceOf()` per attacker-chosen address: [5](#0-4) 
and none of `dimensionsCheck`, `checkOnchainCreation`, or `performHinkalChecks` validate that distinct `erc20TokenAddresses` entries correspond to economically independent balance sources — they only check array-length consistency and that `amountChanges`/`inputNullifiers` are zero when `onChainCreation` is true: [6](#0-5) 

No code in the reachable path (Hinkal.sol, HinkalHelper.sol, DepositOnChainUtxosExternalAction.sol, MainEVMCircuit.circom) enforces that `erc20TokenAddresses[i]` be a registered/whitelisted, economically distinct token; the only constraint found is the raw-value inequality in the circuit, which a purpose-built alias contract trivially satisfies while still sharing/mirroring another entry's real balance.

### Impact Explanation
The attacker mints a shielded on-chain UTXO with no backing collateral, denominated under a token address they control (`TokenB`), while paying only for the real `TokenA` deposit once. If `TokenB` is later made to alias/redeem against a real, valuable token when withdrawn (e.g. its `transfer()`/withdraw path is wired to move real funds out of Hinkal's holdings of the aliased token), the attacker can extract real value they never deposited — direct minting of shielded value without backing, i.e., protocol insolvency. This matches the Critical severity category (minting shielded value without backing). The attack is repeatable for any amount `X` the attacker can afford to deposit once, doubling (or multiplying, with more alias indices) the shielded value minted per real deposit.

### Likelihood Explanation
Preconditions: the attacker must be able to (1) deploy arbitrary token contracts and have their addresses accepted as `erc20TokenAddresses` entries, and (2) route a `DepositOnChainUtxosExternalAction` (or any external action with `onChainCreation=true`) call through `Hinkal.transact` with their own `originalSender`/proof for their own UTXOs — all of which is within the stated attacker capability. No evidence was found in the reachable checks (`dimensionsCheck`, `checkOnchainCreation`, `performHinkalChecks`, `DepositOnChainUtxosExternalAction`) of a token registry/whitelist gate blocking arbitrary attacker-deployed token addresses from being used in `erc20TokenAddresses`; if such a gate exists elsewhere in the codebase (e.g., tied to `erc20TokenRegistryAddress` referenced in `IHinkal.ConstructorArgs`) it was not located within the available index, and its presence would materially reduce feasibility — this should be verified directly against the deployed `ERC20TokenRegistry`/`CircomDataBuilder` logic before relying on this finding.

### Recommendation
Do not snapshot and validate balances as one batch spanning the whole `erc20TokenAddresses` array/whole external action. Either (a) take independent `balanceOf` snapshots immediately bracketing each per-token transfer inside the external action (not merely before/after the entire multi-token call), or (b) require every `erc20TokenAddresses[i]` used with `onChainCreation` to be a registered token from a canonical registry (one canonical address per real asset, with duplicates across a transaction rejected by registry identity, not merely by raw address inequality), and additionally verify actual token receipt (e.g., compare `balanceOf` deltas per-token immediately around that token's own transfer call rather than around the whole batched action).

### Proof of Concept
Foundry test plan:
1. Deploy `TokenA` (standard ERC20, attacker holds `X` tokens, approves Hinkal/`DepositOnChainUtxosExternalAction`).
2. Deploy `TokenB`: `balanceOf(addr)` returns `TokenA.balanceOf(addr)`; `transferFrom` returns `true` without state change.
3. Register `DepositOnChainUtxosExternalAction` in `Hinkal` (owner-only setup step, not attacker-privileged).
4. Craft `CircomData` with `erc20TokenAddresses = [T

### Citations

**File:** contracts/Hinkal.sol (L76-90)
```text
            UTXO[] memory utxoSet;

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

**File:** contracts/Hinkal.sol (L97-146)
```text
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
```

**File:** circuits/MainEVMCircuit.circom (L171-180)
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
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-83)
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

**File:** contracts/HinkalHelper.sol (L173-202)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```

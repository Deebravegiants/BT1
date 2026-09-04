## Answer

The claim is correct and represents a real, critical vulnerability rooted in `EmporiumUpgradeable`'s architecture.

### Equality that should hold but is broken
`external_protocol_beneficiary(getReward/claim/withdraw) == staker_who_originally_deposited(victim)`

In practice it is: `external_protocol_beneficiary == address(EmporiumUpgradeable)` always, regardless of which Hinkal user originates the transaction — because CASE 2 ("Stateless Interaction") makes the call `op.endpoint.call{value: op.value}(op.callData)` directly from the Emporium contract itself: [1](#0-0) 

Any external protocol that gates access by `msg.sender` (e.g. `StakingRewards.getReward()`, `stake()/withdraw()` patterns) sees `msg.sender == address(Emporium)` no matter which Hinkal user submits the `transact()` call. Since `Emporium` is a single shared, well-known contract used by every Hinkal user, a staking position or accrued reward left under `address(Emporium)` between two separate transactions is not cryptographically bound to the depositor's stealth identity — it's a shared pot that the next caller can sweep.

### Path from attacker's call
1. Victim calls `Hinkal.transact()` with an external action pointing to `EmporiumUpgradeable`, whose `EmporiumStack.ops` contains a CASE 2 op calling `StakingContract.stake(amount)`. Funds move from `Hinkal`/`Emporium` into the staking contract, recorded under `staker = address(Emporium)`.
2. Time passes; rewards accrue to `address(Emporium)` inside the staking contract.
3. Attacker (any unprivileged EOA with their own valid proof/UTXOs for gas/relay purposes) submits their own `transact()` call whose CASE 2 op calls `StakingContract.getReward()` (or `claim()`, or even `withdraw(amount)` for the whole principal). Because `msg.sender` from the staking contract's perspective is again `address(Emporium)`, the call succeeds and the reward/principal token lands in `Emporium`'s balance.
4. Back in `runAction`, `balancesAfter - balancesBefore` for that token is positive and unrelated to any `deltaAmountChanges` the attacker paid in (attacker never funded that token), so `handleOut` sweeps it: [2](#0-1) 
5. `handleOut` transfers the swept amount to `msg.sender` (which, at the `EmporiumUpgradeable.runAction` call site, is `Hinkal.sol` itself) and returns a `UTXO` tagged with `circomData.stealthAddressStructure` — a field the **attacker fully controls** in their own proof/circomData.
6. In `Hinkal.transact()`, the real balance increase (`balanceDif`) is reconciled against `circomData.amountChanges[i] + utxoAmount`, both of which are attacker-supplied/self-consistent values the attacker's own proof satisfies (their own new private output note or on-chain UTXO): [3](#0-2) . Nothing here checks that the value being absorbed originated from the victim's earlier `stake()` op — the check is purely an arithmetic balance-diff consistency check for the *current* transaction, with the recipient stealth address chosen entirely by whoever is calling now.

### Why existing guards don't stop it
- `verifyWallet` only checks EIP712 signature and anti-replay of `emporiumMessage`, and only when `stack.signerAddress != address(0)` (CASE 1). CASE 2 requires no signature or authorization tied to the original depositor at all: [4](#0-3) 
- `onlyAllowedRecipient` only gates that `runAction` is called by the allow-listed `Hinkal` contract, not who benefits from the op: [5](#0-4) 
- The CASE 2 selector blocklist only prevents calling `callHinkalWallet`/`doSendToRelay` — it does not restrict which external contract or function (e.g. `getReward`, `claim`, `withdraw`) can be invoked: [6](#0-5) 
- The circuit's `inTotal + amountChanges === outTotal` constraint and `Hinkal.sol`'s balance-diff check only validate the *current caller's* proof self-consistency; they carry no notion of "who owns the externally-staked position," so an attacker with zero real UTXO backing for that token can still mint a valid output note for whatever balance change they trigger.

### Impact
Critical — direct theft of a victim's staking rewards, and in the more severe case (if the op calls `withdraw`/`unstake`), direct theft of the victim's entire staked principal, since the position is custodied under a shared, caller-agnostic `address(Emporium)` with no per-user access control on the external protocol side. This is repeatable against every stateless-CASE-2 op that leaves value resident in an external protocol between transactions (staking, lending, vault deposits, etc.), not just one-off swaps that fully settle balance in the same transaction.

### Title/Summary format

### Title
Attacker can hijack rewards/principal of any position Emporium holds on external protocols via CASE 2 stateless calls - (contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.runAction`'s CASE 2 "Stateless Interaction" executes `op.endpoint.call(...)` directly from the shared `Emporium` contract, so any external protocol that gates by `msg.sender` sees the same identity (`address(Emporium)`) for every Hinkal user. Any position left resident at an external protocol between transactions (e.g. a staking deposit) can therefore be claimed, harvested, or withdrawn by a subsequent, unrelated attacker who routes a `getReward()`/`claim()`/`withdraw()` call through the same Emporium contract and mints the resulting balance increase into their own private UTXO.

### Finding Description
See analysis above: the broken equality is `external_protocol_beneficiary == staker`; in reality it always resolves to `address(Emporium)` regardless of caller identity, because CASE 2 calls are raw, non-delegated external calls made from `Emporium` itself [7](#0-6) , and `handleOut`'s before/after balance sweep [2](#0-1)  combined with `Hinkal.sol`'s generic balance-diff reconciliation [3](#0-2)  credits whoever is currently transacting, not whoever originally deposited.

### Impact Explanation
Theft of shielded value (staking rewards and potentially principal) belonging to the victim, redirected to an attacker-chosen stealth address with zero backing input UTXO on the attacker's side for that token — matches "Critical: direct theft of shielded or in-flight user funds."

### Likelihood Explanation
Requires only that some prior Hinkal user perform a stateless CASE 2 op that leaves value custodied at an external protocol under `address(Emporium)` (a common pattern for staking/lending/vault integrations). The attacker needs only their own unrelated valid proof/UTXOs to pay for gas/relay and craft `circomData.externalActionData` targeting the same external protocol — no special privilege, timing race, or victim cooperation required, and the exploit is repeatable for every subsequent position left behind.

### Recommendation
CASE 2 stateless ops must not be allowed to interact with stateful/positional external protocols under the shared `Emporium` identity without binding the resulting funds to the original depositor. Options: require CASE-2-style claims to be routed only through per-user `IHinkalWallet` proxies (CASE 1, with signature-bound authorization) rather than the shared Emporium address, or disallow persistent multi-transaction external positions entirely (require atomic stake+unstake in one op sequence), or track per-depositor claim rights on-chain in Emporium storage and gate withdrawals/claims against them.

### Proof of Concept
Foundry test: deploy a `MockStakingRewards` contract with `stake(uint256)` (records balance under `msg.sender`) and `getReward()` (transfers accrued reward to `msg.sender`). Victim calls `Hinkal.transact()` with an `EmporiumStack` containing a CASE 2 op `stake(amount)` targeting `MockStakingRewards`. Advance `vm.warp` to accrue rewards. Attacker (with their own funded UTXO/proof for an unrelated token to cover any relay fee) calls `Hinkal.transact()` with a CASE 2 op `getReward()` targeting the same `MockStakingRewards`, listing the reward token in `circomData.erc20TokenAddresses` and setting `circomData.stealthAddressStructure`/`amountChanges` to capture the swept reward as their own private UTXO. Assert: reward token balance of `Emporium`/`Hinkal` increases and a new UTXO commitment is created for the attacker's stealth address, while `MockStakingRewards.rewards(victim)`-equivalent (i.e., the original staker's earned amount) is zeroed out — proving the attacker received the victim's reward with zero backing UTXO burn on the attacker's side for that token.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L91-118)
```text
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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L302-349)
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

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```

**File:** contracts/Hinkal.sol (L134-146)
```text
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

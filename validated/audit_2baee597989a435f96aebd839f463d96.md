### Title
Unprotected `initialize()` in `EmporiumUpgradeable` lets any EOA front-run deployment, become owner, and directly call `runAction()` to steal in-flight funds while bypassing all ZK-proof/nullifier checks - (File: `contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol`)

### Summary
`EmporiumUpgradeable.initialize()` is guarded only by OpenZeppelin's `initializer` modifier (one-time-call protection), not by any caller restriction. Whoever calls it first — on the proxy, before the intended deployer's transaction lands — becomes the contract owner via `_transferOwnership(_owner)` with an `_owner` argument of their own choosing, and can also set `_allowedRecipients` to include themselves.

### Finding Description [1](#0-0) 

```solidity
function initialize(
    IHinkalHelper _hinkalHelper,
    address[] memory _allowedRecipients,
    address _owner
) public initializer {
    __EIP712_init("Emporium", "1.0.0");
    __ExternalActionBase_init(_allowedRecipients); // Initialize parent contract
    ...
    _transferOwnership(_owner);
}
```

`initialize()` has no `onlyOwner`/deployer check — it is open to any address, exactly analogous to the `Controller.__Controller_init()` bug in the referenced report. The only defense (`_disableInitializers()` in the constructor) protects the logic/implementation contract, not the proxy that actually stores state, so the proxy's `initialize()` remains callable by anyone in a race with the legitimate deployment transaction.

Once an attacker wins that race, they are `owner` of the deployed `EmporiumUpgradeable` proxy and can:
1. Call `setAllowedRecipients` (inherited from `ExternalActionBaseUpgradeable`, `onlyOwner`) to add their own address to `_isAllowedRecipient`. [2](#0-1) 
2. Call `runAction()` directly (bypassing `Hinkal.transact`, and therefore bypassing ZK-proof verification, root-hash validation, and nullifier checks entirely), since the only gate is `onlyAllowedRecipient`, which now includes the attacker. [3](#0-2) 
3. Supply a fully attacker-controlled `EmporiumStack` (via `circomData.externalActionData.externalActionMetadata`) and `deltaAmountChanges`, letting the attacker issue arbitrary `op.endpoint.call{value: op.value}(op.callData)` calls and route any resulting positive balance change to themselves via `handleOut` → `transferERC20TokenOrETH(..., msg.sender, ...)`. [4](#0-3) 

This breaks the equality that `runAction` should only ever be reachable through `Hinkal.transact`'s verified proof/root-hash/nullifier pipeline — an attacker who becomes owner via front-running `initialize()` can invoke it with no proof at all, directly stealing whatever ERC20/ETH balance the Emporium contract is holding (e.g., in-flight funds mid-swap).

### Impact Explanation
Critical: this is a proof/nullifier-verification bypass that leads to direct theft of in-flight/shielded user funds held by the `Emporium` contract, and unauthorized asset movement never sanctioned by any prover or wallet signer.

### Likelihood Explanation
The window exists only during the deployment of the `EmporiumUpgradeable` proxy, before the legitimate operator's `initialize()` transaction is mined — a classic front-runnable initializer race, exploitable by any unprivileged EOA/bot monitoring the network without needing any existing role or key.

### Recommendation
Restrict `initialize()` so it can only be executed atomically with proxy deployment (e.g., via a factory that deploys and calls `initialize()` in a single transaction, similar to the pattern used in `HinkalFactory.deployHinkal`), or add explicit `msg.sender` validation against a trusted deployer address inside `initialize()`.

### Proof of Concept
1. Deployer deploys the `EmporiumUpgradeable` implementation and an upgradeable proxy pointing to it, planning to call `initialize(hinkalHelper, allowedRecipients, deployerOwner)` in a follow-up transaction.
2. Attacker observes the pending proxy deployment and submits `proxy.initialize(attackerHinkalHelper, [attackerAddress], attackerAddress)` with higher gas, landing before the legitimate call; the legitimate call then reverts (`initializer` re-entry guard).
3. Attacker is now `owner`, and `attackerAddress` is in `_isAllowedRecipient`.
4. Attacker calls `proxy.runAction(craftedCircomData, craftedDeltaAmountChanges)` directly with a `EmporiumStack` whose `ops` transfer out any token/ETH balance sitting in the Emporium contract, bypassing `Hinkal.transact`'s proof, root-hash, and nullifier checks entirely.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L57-69)
```text
    function initialize(
        IHinkalHelper _hinkalHelper,
        address[] memory _allowedRecipients,
        address _owner
    ) public initializer {
        __EIP712_init("Emporium", "1.0.0");
        __ExternalActionBase_init(_allowedRecipients); // Initialize parent contract
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        $._hinkalHelper = _hinkalHelper;

        _transferOwnership(_owner);
    }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-83)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
        EmporiumStack memory stack = abi.decode(
            circomData.externalActionData.externalActionMetadata,
            (EmporiumStack)
        );
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

**File:** contracts/external-actions/ExternalActionBaseUpgradeable.sol (L64-73)
```text
    function setAllowedRecipients(
        address[] calldata recipients
    ) external onlyOwner {
        ExternalActionBaseStorage storage $ = _getExternalActionBaseStorage();

        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "zero address!");
            $._isAllowedRecipient[recipients[i]] = true;
        }
    }
```

### Title
Unprotected `initialize()` on `EmporiumUpgradeable` allows front-running takeover of the external-action contract - (File: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol)

### Summary
`EmporiumUpgradeable.initialize()` is guarded only by OpenZeppelin's `initializer` modifier, which prevents *re*-initialization but does not restrict *who* may call it first. This is the exact bug class described in the external report for `L2EthToken`: whoever calls the unprotected initializer before the legitimate deployer wins control of privileged state (there, `l2Bridge`; here, `owner` and `_hinkalHelper`).

### Finding Description
`initialize()` sets the allowed-recipients list, the `_hinkalHelper` reference, and transfers ownership, with no check that `msg.sender` is a specific deployer/factory address: [1](#0-0) 

The constructor only calls `_disableInitializers()` on the logic/implementation contract, which does not protect the proxy's own storage from a front-run `initialize()` call: [2](#0-1) 

If the proxy deployment and the `initialize()` call are two separate transactions (standard OZ upgrades pattern unless the proxy constructor atomically encodes the init calldata), an unprivileged EOA can observe the pending proxy deployment/initialize transaction in the mempool and front-run it, passing itself as `_owner` and an attacker-controlled `_hinkalHelper`/`_allowedRecipients` list.

Once owner, the attacker can call the equally unprotected `setAllowedRecipients`: [3](#0-2) 

to add their own EOA/contract to `_isAllowedRecipient`, which is the *only* gate on `runAction`: [4](#0-3) 

In normal operation, `runAction` is only reachable through `HinkalBase._externalTransact`, which is only invoked after Hinkal verifies `circomData.calldataHash` against the actual calldata and validates the ZK proof/nullifiers (`performHinkalChecks` in `HinkalHelper.sol`). By becoming the allowed recipient directly, the attacker calls `runAction` themselves with attacker-crafted `CircomData`/`deltaAmountChanges`, completely bypassing that `calldataHash`/nullifier/proof pipeline, and `handleOut` sends any resulting balance increase straight to `msg.sender`: [5](#0-4) 

This breaks the equality that funds can leave Emporium only via a Hinkal-verified proof/nullifier flow — the attacker extracts any ERC20/ETH balance already sitting in the Emporium contract (from legitimate prior deposits) with no proof at all.

### Impact Explanation
This is a Critical-severity issue: direct theft of shielded/in-flight user funds held in the Emporium contract, and a bypass of the proof/nullifier verification that is supposed to gate every fund movement out of the contract.

### Likelihood Explanation
Exploitability depends entirely on the deployment procedure being out-of-band from `initialize()` (two separate transactions), which is the standard risk pattern for OZ upgradeable proxies and is exactly the scenario flagged in the referenced `L2EthToken` report. The deployment/proxy-wiring scripts themselves are out of scope for this repo, so it cannot be confirmed from in-scope contract code alone whether initialization is performed atomically with proxy construction; this uncertainty should be resolved by inspecting the actual deployment tooling.

### Recommendation
- Deploy the proxy and call `initialize()` atomically in the same transaction (e.g., pass the encoded `initialize` calldata into the proxy's constructor), or
- Restrict `initialize()` to a known, hardcoded factory/deployer address (mirroring the fix suggested in the report — inject a constant deployer address via the templating system), and
- Add a zero-address / already-initialized sanity check on `_hinkalHelper` and `_owner` as defense in depth.

### Proof of Concept
1. Deployer deploys the `EmporiumUpgradeable` implementation and a proxy pointing to it, planning to call `initialize(hinkalHelper, allowedRecipients, deployerOwner)` in a follow-up transaction.
2. Attacker observes the pending proxy deployment and, in the gap before the deployer's `initialize` transaction is mined, sends their own `initialize(attackerHinkalHelper, [], attackerAddress)` with higher gas to be included first.
3. `initializer` modifier only blocks a second call, so the attacker's call succeeds; `attackerAddress` becomes `owner`.
4. Attacker calls `setAllowedRecipients([attackerAddress])`.
5. Attacker calls `runAction` directly with crafted `CircomData` (no valid proof, arbitrary `deltaAmountChanges`) and receives any ERC20/ETH balance already deposited in the Emporium proxy via `handleOut`, with no nullifier or calldata-hash check ever performed.

### Citations

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L52-69)
```text
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

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

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L76-79)
```text
    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external override onlyAllowedRecipient returns (UTXO[] memory) {
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

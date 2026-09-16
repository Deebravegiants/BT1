Based on my investigation, in the production deployment (`DeployIsmp.s.sol`) the testnet `MINTER_ROLE` grant goes to `TokenFaucet`, not to `CallDispatcher` — so I cannot confirm that the canonical deployed `CallDispatcher` is actually granted `MINTER_ROLE` on any live token in production config. The `feeToken.grantMinterRole(address(callDispatcher))` pattern I found is only in the test suite (`evm/tests/foundry/HyperFungibleTokenTest.sol:74`), used to exercise the calldata-execution code path in tests, not a documented or scripted production practice.

### Title
Unrestricted `CallDispatcher.dispatch()` lets any address execute privileged calls if the dispatcher holds a role or balance - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` is a fully public, access-control-free function that executes arbitrary attacker-supplied `Call[]` as the `CallDispatcher` contract itself. [1](#0-0)  It is intended to only be invoked internally, mid-transaction, by `HyperFungibleToken.onAccept` and `IntentsBase._execute`/`IntentGatewayV2.placeOrder` after tokens have been delivered to it. [2](#0-1) [3](#0-2)  But because `dispatch()` has no caller restriction (no `onlyHost`, no `onlyOwner`, no reentrancy/caller check), **any external account can call it directly**, at any time, independent of the ISMP flow.

### Finding Description
This mirrors the reported bug class exactly: a privileged capability (arbitrary `to.call(data)`) is reachable without restriction by anyone who can reach the contract that holds it. In the M-15 report, the DAO proxy held the `EMITTER` role and also exposed an unrestricted arbitrary-call function (`updateProposalAndExecution`), letting a Safe/DAO member weaponize the role via arbitrary calldata. Here, `CallDispatcher` is a single, canonically-deployed, address-shared-across-apps utility contract (deployed once per chain via `DeployIsmp.s.sol:151` and referenced by address in `config.testnet.toml`, `DeployBridgeToken.s.sol:11`, `IntentGatewayV2`/`IntentsBase` params, and `HyperFungibleToken`'s `_dispatcher`). [4](#0-3)  Documentation explicitly instructs integrators to mint/unlock tokens directly to the `CallDispatcher` address so it can spend them via approve-then-swap style calldata, and separately documents the `HyperFungibleTokenImpl` multi-minter role model (`grantMinterRole(account)` restricted only by `DEFAULT_ADMIN_ROLE`) as the intended way to let "multiple contracts" mint. [5](#0-4)  If any deployer or integrator follows the multi-minter pattern and grants `MINTER_ROLE` (or any other privileged role) to the shared `CallDispatcher` address — a plausible and even test-demonstrated configuration (`evm/tests/foundry/HyperFungibleTokenTest.sol:72-74`, `feeToken.grantMinterRole(address(callDispatcher))`) — that role is effectively granted to the public, because `dispatch()` can be called by anyone to encode `Call({to: token, data: abi.encodeWithSelector(mint.selector, attacker, amount)})`, completely bypassing the ISMP host, `onlyHost` guards, and the intended "only mid-fill/mid-mint" invocation context.

### Impact Explanation
If a `MINTER_ROLE`-style privilege is ever granted to the shared `CallDispatcher` address (the exact pattern the test suite exercises and that the "multiple minters" design in `HyperFungibleTokenImpl` invites), this becomes an unbacked/unlimited token mint reachable by any unprivileged caller in a single transaction — a direct match for the "unbacked mint" impact criterion. Separately, even without a role grant, any tokens/ETH the dispatcher is transiently holding mid-fill/mid-mint (or leftover from a reverted/partial operation) can be swept out by any third party who front-runs or races a call to `dispatch()`, since nothing restricts who can drive the dispatcher's balance.

### Likelihood Explanation
Likelihood in the strict-production-config-as-scanned sense is low-to-unconfirmed: the only production script I could inspect (`DeployIsmp.s.sol`) grants `MINTER_ROLE` to `TokenFaucet`, not `CallDispatcher`. However, the vulnerable pattern (unrestricted `dispatch()` + role-bearing shared contract) is real, code-verified, and actively exercised by the test suite, and any deployer/integrator following the documented "multiple minters" idiom with the canonical `CallDispatcher` address would immediately expose it. This is a design flaw in `CallDispatcher`/`HyperFungibleTokenImpl` rather than a one-off misconfiguration.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (e.g., only the `HyperFungibleToken`/`HyperFungibleTokenUpgradeable`/`IntentGatewayV2`/`IntentsBase` instances configured to use it, via `msg.sender` checks or per-app dispatcher instances), or make `CallDispatcher` non-shared (deploy one per app/token) so a role grant to it cannot be leveraged by unrelated external callers. At minimum, documentation should explicitly warn against ever granting privileged roles (mint/burn/admin) to the shared `CallDispatcher` address, and the `HyperFungibleTokenImpl` docs/tests should not model that exact anti-pattern.

### Proof of Concept
1. Deployer grants `MINTER_ROLE` on a `HyperFungibleTokenImpl`-based token to the canonical `CallDispatcher` address (as done for tests in `evm/tests/foundry/HyperFungibleTokenTest.sol:72-74`, and as invited by the "multiple minters" model in `evm/src/utils/HyperFungibleTokenImpl.sol:78-92`).
2. Attacker (any address, no special role) calls:
```solidity
Call ;
calls[0] = Call({to: address(token), value: 0, data: abi.encodeWithSelector(HyperFungibleTokenImpl.mint.selector, attacker, type(uint256).max)});
CallDispatcher(dispatcher).dispatch(abi.encode(calls)); // evm/src/utils/CallDispatcher.sol:44
```
3. `dispatch()` has no access control, so the call succeeds, and `token.mint(attacker, ...)` executes because `msg.sender == address(CallDispatcher)`, which holds `MINTER_ROLE` — attacker unbacked-mints arbitrary tokens with no ISMP message, no host interaction, and no restriction whatsoever. [1](#0-0)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L301-306)
```text
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/script/DeployIsmp.s.sol (L151-167)
```text
        CallDispatcher callDispatcher = new CallDispatcher{salt: salt}();
        BandwidthManager bandwidthManager = new BandwidthManager{salt: salt}(admin);
        bandwidthManager.setHost(address(host));
        
        vm.stopBroadcast();

        // ============= Write addresses to config =============
        if (!isMainnet) {
            config.set("TOKEN_FAUCET", address(faucet));
            config.set("FEE_TOKEN", feeToken);
        }
        config.set("HOST", address(host));
        config.set("ECDSA_BEEFY", address(ecdsaBeefy));
        config.set("SP1_BEEFY", address(sp1Beefy));
        config.set("HANDLER_V2", address(handler));
        config.set("CONSENSUS_ROUTER", address(consensusRouter));
        config.set("CALL_DISPATCHER", address(callDispatcher));
```

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L78-92)
```text
    /**
     * @notice Grants minter role to an address
     * @param account The address to grant the minter role to
     */
    function grantMinterRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(MINTER_ROLE, account);
    }

    /**
     * @notice Grants burner role to an address
     * @param account The address to grant the burner role to
     */
    function grantBurnerRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(BURNER_ROLE, account);
    }
```

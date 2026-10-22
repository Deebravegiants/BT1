# [M] Admin will not be able to up-

## Summary
Severity: Medium
Contest weight: 0.6073
Dataset id: 2587
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AssetFactory and FlashSwapRouter inherit the UUPSUpgradeable contract in order to be upgradeable. However, AssetFactory::initialize(), FlashSwapRouter::initialize(), AssetFactory::_authorizeUpgrade() and FlashSwapRouter::_authorizeUpgrade() have the notDelegated, which means they can not be called in the context of a proxy, hence they can not be upgradeable. This renders the inherited UUPSUpgradeable useless and the 2 contracts will not be upgradeable. Additionally, the AssetFactory and FlashSwapRouter contracts are not deployed behind proxies, meaning that this problem would be noticed when trying to upgrade and failing. In AssetFactory.sol:48, AssetFactory.sol:195, FlashSwapRouter.sol:32 and FlashSwapRouter.sol:41 the notDelegated modifiers are used. Internal pre-conditions None. External pre-conditions None. Attack Path Admin tries to upgrade the AssetFactory and FlashSwapRouter contracts but fails. The UUPSUpgradeable contract is rendered useless, which means the AssetFactory and FlashSwapRouter contracts can not be upgraded. This leads to breaking major functionality as well as the possibility of stuck/lost funds.

## Proof of Concept
FlashSwapRouter
```solidity
contract RouterState is IDsFlashSwapUtility, IDsFlashSwapCore, OwnableUpgradeable, UUPSUpgradeable, IUniswapV2Callee {
    ...
    function initialize(address moduleCore, address _univ2Router) external initializer notDelegated {
        __Ownable_init(moduleCore);
        __UUPSUpgradeable_init();
        univ2Router = IUniswapV2Router02(_univ2Router);
    }
    ...
    function _authorizeUpgrade(address newImplementation) internal override onlyOwner notDelegated {}
}
```
AssetFactory
```solidity
contract AssetFactory is IAssetFactory, OwnableUpgradeable, UUPSUpgradeable {
    ...
    function initialize(address moduleCore) external initializer notDelegated {
        __Ownable_init(moduleCore);
        __UUPSUpgradeable_init();
    }
    ...
    function _authorizeUpgrade(address newImplementation) internal override onlyOwner notDelegated {}
}
```

## Recommendation
Remove the notDelegated modifiers.

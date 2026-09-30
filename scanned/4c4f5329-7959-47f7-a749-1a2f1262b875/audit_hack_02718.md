# [M] No functionality to change ownership of contracts

## Summary
Severity: Medium
Reporter: smit_rajput
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionProxy.sol#L29
Type: audit-issue

## Details
# No functionality to change ownership of contracts

## Summary
In the entire system of Auction + Queue + Vault contracts, the functionality to change ownership of these contracts is not implemented. Ownership is only set once and is assumed to never have the need to be changed. And this assumption will be incorrect in case the private key of this single owner gets compromised, and the ownership certainly needs to change, to avoid the entire system from getting compromised and loss of ALL the funds in the contracts.

## Vulnerability Detail
Ownership of Action, Queue and Vault contracts only gets set once in the constructors of `AuctionProxy.sol`, `QueueProxy.sol` and `VaultDiamond.sol`, when these contracts are deployed. There is NO way to change this ownership in case the current ownership gets compromised.

## Impact
Medium severity. There is no direct loss of funds, but potentially the entire system getting compromised, in case the private keys of the current owner get compromised, and there is no way to change the ownership of the contracts.

## Code Snippet
1. AuctionProxy.sol: [L29](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionProxy.sol#L29)
```javascript
    constructor(
        uint256 minSize,
        address exchange,
        address implementation
    ) {
        AuctionStorage.Layout storage l = AuctionStorage.layout();
        l.Exchange = IExchangeHelper(exchange);
        l.minSize = minSize;

        OwnableStorage.layout().setOwner(msg.sender);
        UpgradeableProxyStorage.layout().setImplementation(implementation);
    }
```
2. QueueProxy.sol: [L42](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueProxy.sol#L42)
```javascript
    constructor(
        uint256 maxTVL,
        address exchange,
        address implementation
    ) {
        {
            QueueStorage.Layout storage l = QueueStorage.layout();
            l.Exchange = IExchangeHelper(exchange);
            l.maxTVL = maxTVL;
        }

        {
            ERC165Storage.Layout storage l = ERC165Storage.layout();
            l.setSupportedInterface(type(IERC165).interfaceId, true);
            l.setSupportedInterface(type(IERC1155).interfaceId, true);
        }

        OwnableStorage.layout().setOwner(msg.sender);
        UpgradeableProxyStorage.layout().setImplementation(implementation);
    }
```
3. VaultDiamond.sol: [L64](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultDiamond.sol#L64)
```javascript
    constructor(VaultStorage.InitProxy memory initProxy) {
        address asset;

        {
            VaultStorage.Layout storage l = VaultStorage.layout();
           ...
        }

        {
            ERC20MetadataStorage.Layout storage l =
                ERC20MetadataStorage.layout();
            l.setName(initProxy.name);
            l.setSymbol(initProxy.symbol);
            l.setDecimals(18);
        }

        ERC4626BaseStorage.layout().asset = asset;
        OwnableStorage.layout().setOwner(msg.sender);
    }
```
The above 3 lines are the ONLY places where the ownership of the core contracts of Auction, Queue and Vault gets set.

## Tool used
Manual Review

## Recommendation
Add this snippet in `AuctionProxy.sol`, `QueueProxy.sol` and `VaultDiamond.sol`, right after constructor, and ensure to not use this function name i.e. `changeOwnership()` in any of the current and future implementation contracts of Auction, Queue and Vault, to avoid function shadowing between the proxy and implementation contracts.
```javascript
    function changeOwnership(address account) external onlyOwner {
        require(_owner() != account, "_owner() == account");
        _transferOwnership(account);
    }
```

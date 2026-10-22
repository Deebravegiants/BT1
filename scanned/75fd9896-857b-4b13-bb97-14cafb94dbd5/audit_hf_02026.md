# [M] Redundant Check in Market::constructor()

## Summary
Severity: Medium
Contest weight: 0.5718
Dataset id: 11556
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As we introduced in Section 3.1, 88mph pools the deposits together and deposits them to different markets to earn interests. Take AaveMarket for example, the deployer has to provide _provider, _aToken and _stablecoin to the constructor which will be used in deposit and withdraw. The constructor has to make sure these addresses are not address(0) and they are contracts.
```solidity
constructor (
    address _provider,
    address _aToken,
    address _stablecoin
) public {
    // Verify input addresses
    require(
        _provider != address(0) &&
        _aToken != address(0) &&
        _stablecoin != address(0),
        "AaveMarket: An input address is 0"
    );
    require(
        _provider.isContract() &&
        _aToken.isContract() &&
        _stablecoin.isContract(),
        "AaveMarket: An input address is not a contract"
    );
    provider = ILendingPoolAddressesProvider(_provider);
    stablecoin = ERC20(_stablecoin);
    aToken = ERC20(_aToken);
}
```
However, address(0) won't pass the check of isContract(). So the first check on address(0) is redundant. Therefore, the first require could be safely removed. The same problem exists in CompoundERC20Market, HarvestMarket and YVaultMarket.

## Recommendation
Remove the first check that the input address shouldn't be address(0).
```solidity
constructor (
    address _provider,
    address _aToken,
    address _stablecoin
) public {
    require(
        _provider.isContract() &&
        _aToken.isContract() &&
        _stablecoin.isContract(),
        "AaveMarket: An input address is not a contract"
    );
    provider = ILendingPoolAddressesProvider(_provider);
    stablecoin = ERC20(_stablecoin);
    aToken = ERC20(_aToken);
}
```

# [H] Missing Proper Access Control

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Some functions do not have proper access control and are `public`, meaning that anyone can call them. This will result in system take over depending on how critical those functionalities are. 

#### Examples

Anyone can set `IDOLContract` in `MainContracts.Auction.sol`, which is a critical aspect of the auction contract, and it cannot be changed after it is set:


**code/MainContracts/contracts/Auction.sol:L144-L148**
```solidity
 */
function setIDOLContract(address contractAddress) public {
    require(address(_IDOLContract) == address(0), "IDOL contract is already registered");
    _setStableCoinContract(contractAddress);
}
```

#### Recommendation

Make the `setIDOLContract()` function `internal` and call it from the constructor, or only allow the `deployer` to set the value.

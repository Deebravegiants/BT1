# [M] Should check if the asset already exists when adding a new asset

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The public function `includeAsset`


**src/Loihi.sol:L128-L130**
```solidity
function includeAsset (address _numeraire, address _nAssim, address _reserve, address _rAssim, uint256 _weight) public onlyOwner {
    shell.includeAsset(_numeraire, _nAssim, _reserve, _rAssim, _weight);
}
```

Calls the internal `includeAsset` implementation


**src/Controller.sol:L72**
```solidity
function includeAsset (Shells.Shell storage shell, address _numeraire, address _numeraireAssim, address _reserve, address _reserveAssim, uint256 _weight) internal {
```

But there is no check to see if the asset already exists in the list. Because the check was not done, `shell.numeraires` can contain multiple identical instances.


**src/Controller.sol:L80**
```solidity
shell.numeraires.push(_numeraireAssimilator);
```

#### Recommendation

Check if the `_numeraire` already exists before invoking `includeAsset`.

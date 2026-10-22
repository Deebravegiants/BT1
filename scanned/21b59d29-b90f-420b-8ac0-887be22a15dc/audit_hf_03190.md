# [M] Early depositors to DnGmxSeniorVault can ma-

## Summary
Severity: Medium
Contest weight: 0.5672
Dataset id: 17764
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To calculate the exchange rate for shares in DnGmxSeniorVault it divides the total supply of shares by the totalAssets of the vault. The first deposit can mint a very small number of shares then donate aUSDC to the vault to grossly manipulate the share price. When later depositor deposit into the vault they will lose value due to precision loss and the adversary will profit.
```solidity
function convertToShares(uint256 assets) public view virtual returns (uint256) {
    uint256 supply = totalSupply(); // Saves an extra SLOAD if totalSupply is non-zero.
    return supply == 0 ? assets : assets.mulDivDown(supply, totalAssets());
}
```
Share exchange rate is calculated using the total supply of shares and the totalAsset. This can lead to exchange rate manipulation. As an example, an adversary can mint a single share, then donate 1e8 aUSDC. Minting the first share established a 1:1 ratio but then donating 1e8 changed the ratio to 1:1e8. Now any deposit lower than 1e8 (100 aUSDC) will suffer from precision loss and the attackers share will benefit from it. This same vector is present in DnGmxJuniorVault. Adversary can effectively steal funds from later users

## Recommendation
Initialize should include a small deposit, such as 1e6 aUSDC that mints the share to a dead address to permanently lock the exchange rate:
```solidity
aUsdc.approve(address(pool), type(uint256).max);
IERC20(asset).approve(address(pool), type(uint256).max);
deposit(1e6, DEAD_ADDRESS);
```

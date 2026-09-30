# [M] Initial user of voltGNS vault can abuse round-

## Summary
Severity: Medium
Contest weight: 0.5899
Dataset id: 19781
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC4626 vault contracts suffer from a commonly known vulnerability due to massively skew the ratio of shares to assets with a large "donation", and can profit off of later users.
In VoltGNS vault, the deposit function has no minimum deposit limit or burn.
#L58-L69 This calls the ERC4626 deposit function which is defined as
```solidity
function deposit(uint256 assets, address receiver) public virtual override returns (uint256) {
    require(assets <= maxDeposit(receiver), "ERC4626: deposit more than max");
    uint256 shares = previewDeposit(assets);
    _deposit(_msgSender(), receiver, assets, shares);
    return shares;
}
```
Which eventually calls _convertToShares to calculate the number of shares,
```solidity
function _convertToShares(uint256 assets, Math.Rounding rounding) internal view virtual returns (uint256 shares) {
    uint256 supply = totalSupply();
    return
        (assets == 0 || supply == 0)
            ? _initialConvertToShares(assets, rounding)
            : assets.mulDiv(supply, totalAssets(), rounding);
}
```
This function takes into account the totalAssets(), which has been overridden and s/voltGNS.sol#L260-L263 returning the sum of current balance and staked amount.
However, due to rounding errors, an attacker who deposits to a fresh vault can skew the ratio by transferring in a large quantity of GNS tokens by following these steps
1. Attacker deposits 1 wei of GNS token, minting 1 wei of voltGNS share
2. Attacker then sends a large amount (1e18 wei) of GNS tokens to the vault.
3. Normal user comes and deposits 2e18 wei of GNS tokens. Shares calculated = 2e18 * 1 / (1e18+1) = 1 wei
4. User only gets minted 1 wei of voltGNS token, giving him claim to only half the vault, which has 3e18 wei tokens, instantly losing him 0.5e18 tokens which is profited by the attacker.
Exploit by first user of vault. Loss of tokens by other users

## Recommendation
Burn the first (if totalSupply() == 0) 10000wei of minted shares by sending them to address 0. This will make the cost to pull of this attack unfeasable.

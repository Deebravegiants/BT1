# [M] voltGNS.mint doesn't allow to mint for first

## Summary
Severity: Medium
Contest weight: 0.3984
Dataset id: 19782
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
voltGNS.mint doesn't allow to mint for first depositor
#L71-L83
```solidity
function mint(uint256 shares, address receiver) public virtual override returns (uint256) {
    require(totalAssets() > 0);
    compound();
    shares = sendMintFees(shares);
    uint256 assets = super.mint(shares, receiver);
    require(totalAssets() <= maxGNSDeposited(), "GNS deposits more than max");
    stakeGNS();
    return assets;
}
```
voltGNS.mint doesn't allow to call itself, when totalAssets is 0. I believe that there is no reasons for that and it just creates bad experience for the first user who will try to mint shares for himself in the voltGNS.
If fore some reasons i am wrong and there is reason why to limit first depositor to call mint then there is a simple way to avoid that. Just donate 1 wei of GNS into voltGNS and then call mint.
First depositor can't mint shares.

## Recommendation
Allow deposit when totalAssets is 0.

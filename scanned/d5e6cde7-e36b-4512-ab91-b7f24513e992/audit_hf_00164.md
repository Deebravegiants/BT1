# [M] `Basket.sol#handleFees`

## Summary
Severity: Medium
Contest weight: 0.4281
Dataset id: 906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function handleFees() private {
    if (lastFee == 0) {
        lastFee = block.timestamp;
    } else {
        uint256 startSupply = totalSupply();

        uint256 timeDiff = (block.timestamp - lastFee);
        uint256 feePct = timeDiff * licenseFee / ONE_YEAR;
        uint256 fee = startSupply * feePct / (BASE - feePct);

        _mint(publisher, fee * (BASE - factory.ownerSplit()) / BASE);
        _mint(Ownable(address(factory)).owner(), fee * factory.ownerSplit() / BASE);
        lastFee = block.timestamp;

        uint256 newIbRatio = ibRatio * startSupply / totalSupply();
        ibRatio = newIbRatio;

        emit NewIBRatio(ibRatio);
    }
}
```

`timeDiff * licenseFee` can be greater than `ONE_YEAR` when `timeDiff` and/or `licenseFee` is large enough, which makes `feePct` to be greater than `BASE` so that `BASE - feePct` will revert on underflow.

## Proof of Concept
1. Create a basket with a `licenseFee` of `1e19` or 1000% per year and mint 1 basket token;
2. The basket remain inactive (not being minted or burned) for 2 months;
3. Calling `mint` and `burn` reverts at `handleFees()`.

## Recommendation
Limit the max value of `feePct`.

The finding is valid, there are conditions that would cause `feePct` to be greater than `BASE`

The conditions to trigger this seem to be:

* Wait enough time
* Have a high enough fee

Because this can happen under specific conditions, I will grade this finding as medium severity:

I would highly recommend the sponsor to consider the possibility of capping the `licenseFee` to make it easier to predict cases in which the operation can revert

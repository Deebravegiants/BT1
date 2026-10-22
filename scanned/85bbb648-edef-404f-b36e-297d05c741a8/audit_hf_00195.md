# [M] `Basket.sol#mint

## Summary
Severity: Medium
Contest weight: 0.0897
Dataset id: 1027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
function mint(uint256 amount) public nonReentrant override {
        mintTo(amount, msg.sender);
    }
    
    function mintTo(uint256 amount, address to) public nonReentrant override {
        require(auction.auctionOngoing() == false);

The `mint()` method is malfunction because of the extra `nonReentrant` modifier, as `mintTo` already has a `nonReentrant` modifier.

## Recommendation
Change to:
    
    function mint(uint256 amount) public override {
        mintTo(amount, msg.sender);
    }

Mint is factually broken, definitely an oversight. I don't think high severity is correct here though as since no-one can mint, no funds are at risk. I'll go with medium severity as per the docs:
    
    2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.

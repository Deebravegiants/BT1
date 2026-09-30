# [M] Inconsistency in fees

## Summary
Severity: Medium
Contest weight: 0.6850
Dataset id: 17230
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the seller cancels before the sale startTime then all funds should be moved to saleReceiver without any deduction (Assuming seller has sent some ETH accidentally before sell start). But in `FixedPrice.sol` contract, fees are deducted even when seller cancels before the sale startTime which could lead to loss of funds.

## Proof of Concept
1. A new sale is started
2. Seller selfdestructed one of his personal contracts and by mistake gave this sale contract as receiver. This forcefully sends the remaining 20 ETH to the `FixedPrice.sol` contract.
3. Seller realizes his mistake and tries to cancel the sale as sale as not yet started using the `cancel` function.
```solidity
    function cancel() external onlyOwner {
            require(block.timestamp < sale.startTime, "TOO LATE");
            _end(sale);
        }
```
4. This internally calls the `_end` function
```solidity
    function _end(Sale memory _sale) internal {
            emit End(_sale);
            ISaleFactory(factory).feeReceiver().transfer(address(this).balance / 20);
            selfdestruct(_sale.saleReceiver);
        }
```
5. The `_end` function deducts fees of 20/20=1 ETH even though seller has cancelled before the sale starts.

## Recommendation
Revise the `cancel` function
```solidity
    function cancel() external onlyOwner {
            require(block.timestamp < sale.startTime, "TOO LATE");
            emit End(_sale);
            selfdestruct(_sale.saleReceiver);
        }
```

I consider Medium severity appropriate because fees are sent to the receiver even though a sale has not started yet. This also clearly deviates from the implementation in the `FixedPrice` contract, where fees are not sent in case the owner cancels a sale.

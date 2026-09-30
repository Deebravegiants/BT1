# [M] Improved ETH Transfer in UnwrapTokenV1::_transferEth()

## Summary
Severity: Medium
Contest weight: 0.4190
Dataset id: 13372
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UnwrapTokenV1 contract provides an interface, i.e., claimWithdraw(), for the user to claim the allocated ETH. The ETH is transferred to the user by calling the internal _transferEth() routine. While reviewing the implementation of the _transferEth() routine, we notice that the ETH transfer may fail because of the possible Out-of-Gas. To elaborate, we show below the code snippet of the _transferEth() routine, which is called from the claimWithdraw() routine to transfer ETH to its claimer. As we can see the _transferEth() routine directly calls the native transfer() routine (line 337) to transfer ETH. However, it comes to our attention that the transfer() is not recommend to use any more since the EIP-1884 may increase the gas cost and the 2300 gas limit may be exceeded. Check the following blog stop-using-soliditys-transfer-now for the detail why the transfer() is not recommend any more. As a result, the transfer() may revert and the ETH is locked in the contract. Based on this, we suggest to use call() directly with value attached to transfer ETH.

```solidity
function _transferEth(address _recipient, uint256 _ethAmount) internal virtual {
    payable(_recipient).transfer(_ethAmount);
}
```

## Recommendation
Revisit the _transferEth() routine to transfer ETH using call().

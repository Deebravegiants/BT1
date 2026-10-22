# [M] `MerkleDropFactory.depositTokens

## Summary
Severity: Medium
Contest weight: 0.4671
Dataset id: 6678
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function `depositTokens()` does not first check to ensure that the `treeIndex` exists.

The impact is that we will attempt to transfer from the zero address to this address. If the transfer succeeds (which it currently does not since we use `IERC20.transferFrom()`) then the `tokenBalance` of this index will be increased.

This will be an issue if the contract is updated to use OpenZeppelin’s `safeTransferFrom()` function. This update may be necessary to support non-standard ERC20 tokens such as USDT.

If the update is made then `merkleTree.tokenAddress.safeTransferFrom(msg.sender, address(this), value), "ERC20 transfer failed");` will succeed if `merkleTree.tokenAddress = address(0)` since `safeTransferFrom()` succeeds against the zero address.

## Proof of Concept
There are no checks the `treeIndex` is valid.
```solidity
function depositTokens(uint treeIndex, uint value) public {
    // storage since we are editing
    MerkleTree storage merkleTree = merkleTrees[treeIndex];

    // bookkeeping to make sure trees don't share tokens
    merkleTree.tokenBalance += value;

    // transfer tokens, if this is a malicious token, then this whole tree is malicious
    // but it does not effect the other trees
    require(IERC20(merkleTree.tokenAddress).transferFrom(msg.sender, address(this), value), "ERC20 transfer failed");
    emit TokensDeposited(treeIndex, merkleTree.tokenAddress, value);
}
```

## Recommendation
Consider adding the check to ensure `0 < treeIndex <= numTrees` in `depositTokens()`.

Technically valid, but this harms no one but the caller, and incorrectly entering arguments is not in scope. 
File this under code style.

[illuzen (FactoryDAO) resolved](https://github.com/code-423n4/2022-05-factorydao-findings/issues/59#issuecomment-1145529595):

<https://github.com/code-423n4/2022-05-factorydao/pull/3>

Maintaining severity as validating treeIndex isn’t out of bounds seems within the appropriate expectations of input validation.

FYI, the call will not succeed because OZ’s safeTransferFrom() will revert if target isn’t an EOA. Solmate on the other hand will not. <https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol#L110>  
<https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Address.sol#L135>  
<https://github.com/Rari-Capital/solmate/blob/main/src/utils/SafeTransferLib.sol#L9>

@HickupHH3 - ‘target’ in openzeppelin’s address library refers to the contract making the call. In other words, merkleTree.tokenAddress. So the call will succeed.

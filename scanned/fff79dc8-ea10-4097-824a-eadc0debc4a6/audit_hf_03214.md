# [H] Bull can prevent settleContract()

## Summary
Severity: High
Contest weight: 0.5802
Dataset id: 17817
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The bull can intentionally cause out-of-gas and revert the transaction and prevent settleContract(). As IERC721(order.collection).safeTransferFrom() is used in settleContract() which will call IERC721Receiver(to).onERC721Received() when the to address is an contract. This gives the bull a chance to intentionally prevent the transaction from happening by consuming a lot of gas and revert the whole transaction. The bear (victim) can not settleContract() therefore cannot exercise their put option rights. The bull (attacker) always wins.

## Recommendation
```solidity
function settleContract(Order calldata order, uint tokenId) public nonReentrant {
    bytes32 orderHash = hashOrder(order);
    // ContractId
    uint contractId = uint(orderHash);
    address bear = bears[contractId];
    // Check that only the bear can settle the contract
    require(msg.sender == bear, "ONLY_BEAR");
    // Check that the contract is not expired
    require(block.timestamp < order.expiry, "EXPIRED_CONTRACT");
    // Check that the contract is not already settled
    require(!settledContracts[contractId], "SETTLED_CONTRACT");
    address bull = bulls[contractId];
    // Try to transfer the NFT to the bull (needed in case of a malicious bull that block transfers)
    try IERC721(order.collection).safeTransferFrom(bear, bull, tokenId) {} 
    catch (bytes memory) {
        // Transfer NFT to BvbProtocol
        IERC721(order.collection).safeTransferFrom(bear, address(this), tokenId);
        // Store that the bull has to retrieve it
        withdrawableCollectionTokenId[order.collection][tokenId] = bull;
    }
    uint bearAssetAmount = order.premium + order.collateral;
    if (bearAssetAmount > 0) {
        // Transfer payment tokens to the Bear
        IERC20(order.asset).safeTransfer(bear, bearAssetAmount);
    }
    settledContracts[contractId] = true;
    emit SettledContract(orderHash, tokenId, order);
}
```

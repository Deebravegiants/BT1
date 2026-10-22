# [H] DOS in the claimWithdraw function due to an

## Summary
Severity: High
Contest weight: 0.3847
Dataset id: 10041
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The claimWithdrawal function has an incorrect check of lastFinalizedRequestId, which lead to a DOS vulnerability in the EEtherAdapter.claimWithdraw function. if (_requestId < ETHERFI_WITHDRAW_NFT.lastFinalizedRequestId()) revert RequestInQueue(); Let's discuss how WithdrawRequestNFT handles withdrawal request IDs. When requestWithdraw is called, the nextRequestId is increased by one. uint256 requestId = nextRequestId++; For a user to successfully call the claimWithdraw function, the admin of WithdrawRequestNFT must call finalizeRequests with our requestId: function finalizeRequests(uint256 requestId) external onlyAdmin { lastFinalizedRequestId = uint33(requestId); } So, if a requestId is created and the admin finalizes our request id, then the user will be able to claim the withdrawal amount. However, the issue lies in the fact that EEtherAdapter.claimWithdrawal checks whether _requestId >= ETHERFI_WITHDRAW_NFT.lastFinalizedRequestId(), otherwise the call will fail. if (_requestId < ETHERFI_WITHDRAW_NFT.lastFinalizedRequestId()) revert RequestInQueue(); However, when we examine the WithdrawRequestNFT.claimWithdrawal function, we see a completely different check: require(tokenId < nextRequestId, "Request does not exist"); --> require(tokenId <= lastFinalizedRequestId, "Request is not finalized"); require(ownerOf(tokenId) != address(0), "Already Claimed"); From this, we can conclude that a user will only be able to call the claimWithdrawal function when requestId = lastFinalizedRequestId; otherwise, the call will fail. Now, if we examine WithdrawRequestNFT on Etherscan, we can obtain the Most importantly, the admin calls lastFinalizedRequestId for each request ID, and the user can claim the withdrawal request ID later, meaning the main condition is that tokenId <= lastFinalizedRequestId. This will result in a situation where if the admin calls lastFinalizedRequestId with our request ID and then with the next one, we will never be able to claim the withdrawal by this request ID. Users will not lose their shares or receive the expected ETH, but this will impact EEtherAdapter as a whole because the totalQueueEth will be increased by the requested withdrawal amount, and it will not be possible to decrease it due to the DOS of the claimWithdraw function. As EEtherAdapter is not an upgradable smart contract, I consider this issue to be of high severity.

## Recommendation
Consider removing this check altogether, or you can implement it exactly as EtherFi does:
```diff
-if (_requestId < ETHERFI_WITHDRAW_NFT.lastFinalizedRequestId()) revert
RequestInQueue();
+if (_requestId > ETHERFI_WITHDRAW_NFT.lastFinalizedRequestId()) revert
RequestInQueue();
```

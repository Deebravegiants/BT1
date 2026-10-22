# [H] Revisited Logic Of OpenSkyApeCoinStakingHelper::depositBAYC()

## Summary
Severity: High
Contest weight: 0.7870
Dataset id: 12636
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To support the BAYC/MAYC loans that are in the borrowing status to participate in Ape Coin staking through the flashClaim() method, the OpenSkyLoan and TransferAdapterERC721Default contracts have implemented the flashClaim ABI for Instant Loans and Bespoke Loans, respectively. Users can call the corresponding contract's ABI based on the type of loan.
In the original implementation of the OpenSkyApeCoinStakingHelper contract, the team notices that the depositBAYC() routine does not validate the recipient address when transferring Ape Coins. To elaborate, we show the related routine from the OpenSkyApeCoinStakingHelper contract.
```solidity
function depositBAYC(IApeCoinStaking.SingleNft[] calldata _nfts, address _recipient)
    public
    onlySelf
{
    uint256 amount;
    for (uint256 i; i < _nfts.length; ++i) {
        amount += _nfts[i].amount;
    }
    apeCoin.safeTransferFrom(_recipient, address(this), amount);
    apeCoin.safeApprove(address(apeCoinStaking), amount);
    apeCoinStaking.depositBAYC(_nfts);
}
```
For example, Alice approves 200 Ape Coins to the OpenSkyApeCoinStakingHelper contract and then uses flashClaim() to call depositBAYC() and stakes 100 Ape Coins. At this point, if a bad actor knows that Alice has approved 200 Ape Coins and that there are still 100 Ape Coins that can be transferred by the OpenSkyApeCoinStakingHelper, they could also use flashClaim() to call depositBAYC() and stake 100 Ape Coins using Alice's 100 Ape Coins. To solve this issue, the team splits the OpenSkyApeCoinStakingHelper contract into separate contracts, with each operation being implemented in its own contract. This would allow each operation to perform parameter validation. However, when reviewing this change, we notice the problem is still there. To elaborate, we show the related routine from the OpenSkyApeCoinStakingHelper contract.
```solidity
function executeOperation(
    address[] calldata nftAddresses,
    uint256[] calldata tokenIds,
    address initiator,
    address operator,
    bytes calldata params
) external override returns (bool) {
    require(msg.sender == operator, "PARAMS_ERROR");
    (uint256[] memory baycs, address recipient) = abi.decode(params, (uint256[], address));
    apeCoinStaking.claimBAYC(baycs, recipient);
    for (uint256 i; i < nftAddresses.length; i++) {
        IERC721(nftAddresses[i]).approve(operator, tokenIds[i]);
    }
    return true;
}
```
It comes to our attention that within the executeOperation() routine, bad actors can write a contract to transfer his BAYC to the helper contract without using flashClaim(), and then directly call executeOperation() to use Alice's Ape Coins to do staking. Afterwards, bad actors can transfer their BAYC back to themselves as the operator is the same with msg.sender.

## Recommendation
It is necessary to add an additional msg.sender verification to limit the ability to call executeOperation() to only the OpenSkyLoan and TransferERC721Default contracts.

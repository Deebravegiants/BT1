# [M] Lack of Usage of safeTransferFrom for External Token Interactions

## Summary
Severity: Medium
Contest weight: 0.4159
Dataset id: 14739
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a potentially unsafe call to PaymentToken.transferFrom() on line [128] of OTC.sol .
```solidity
/// @notice Requests IndexToken for PaymentToken
/// @param paymentTokenAmount amount of PaymentToken to deposit
/// @param indexTokenAmount amount of IndexToken to receive
function requestIndexToken(uint256 paymentTokenAmount, uint256 indexTokenAmount)
    external
    onlyUser
    returns (uint256)
{
    PaymentToken.transferFrom(msg.sender, depositAddress, paymentTokenAmount); // reverts on failure
    requests.push(
        Request(msg.sender, paymentTokenAmount, indexTokenAmount, RequestStatus.PENDING, 2**256 - 1, depositAddress)
    );
    uint256 nonce = requests.length - 1;
    emit RequestIndexToken(nonce, msg.sender, depositAddress, paymentTokenAmount, indexTokenAmount);
    return nonce;
}
```
Although this call is expected to revert on failure, this cannot be assumed of an arbitrary paymentToken which may not fully comply with ERC20 specifications. As such, failed payments may manage to successfully initiate an index token request.

## Recommendation
Use OpenZeppelin’s SafeERC20 wrapper function on line [128] of OTC.sol .
Alternatively, new OTC deployments for each paymentToken should be carefully reviewed and whitelisted by the protocol team. This reduces gas costs on transfers, but retains an avoidable long term risk in the contracts.

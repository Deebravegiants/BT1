# [M] `PrivatePool.flashLoan`

## Summary
Severity: Medium
Contest weight: 0.5934
Dataset id: 18349
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Instead of taking the fee from the receiver of the flashloan callback, it pulls it from `msg.sender`.

As specified in [EIP-3156](https://eips.ethereum.org/EIPS/eip-3156#lender-specification):

> “After the callback, the flashLoan function MUST take the amount + fee token from the receiver, or revert if this is not successful.”

This will be an unexpected loss of funds for the caller if they have the pool pre-approved to spend funds (e.g. they previously bought NFTs) and are not the owner of the flashloan contract they use for the callback.

Additionally, for ETH pools, it expects the caller to pay the fee upfront. But, the fee is generally paid with the profits made using the flashloaned tokens.

## Proof of Concept
If `baseToken` is ETH, it expects the fee to already be sent with the call to `flashLoan()`. If it’s an ERC20 token, it will pull it from `msg.sender` instead of `receiver`:
    
```solidity
function flashLoan(IERC3156FlashBorrower receiver, address token, uint256 tokenId, bytes calldata data)
    external
    payable
    returns (bool)
{
    // ...

    // calculate the fee
    uint256 fee = flashFee(token, tokenId);

    // if base token is ETH then check that caller sent enough for the fee
    if (baseToken == address(0) && msg.value < fee) revert InvalidEthAmount();
    
    // ...

    // transfer the fee from the borrower
    if (baseToken != address(0)) ERC20(baseToken).transferFrom(msg.sender, address(this), fee);

    return success;
}
```

## Recommendation
Change to:
    
```solidity
uint initialBalance = address(this).balance;
// ... 

if (baseToken != address(0)) ERC20(baseToken).transferFrom(receiver, address(this), fee);
else require(address(this).balance - initialBalance == fee);
```

I have considered downgrading to QA for the ETH aspect as technically there is no EIP for ETH flashloans (FL EIP is only for ERC20s).

That said, the way payment is pulled in ERC20s is breaking the spec, and for this reason am awarding Medium Severity.

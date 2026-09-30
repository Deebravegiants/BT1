# [M] Possible loss of funds, transfer functions can

## Summary
Severity: Medium
Contest weight: 0.6979
Dataset id: 23020
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Possible loss of funds, transfer functions can silently fail
Union Protocol's contracts are expected to be used USDT, USDC and DAI. The contracts will be deployed on Any EVM compatible chain which also includes Ethereum mainnet itself. Both of these details are mentioned in contest readme.
This issue is specifically for tokens like USDT and similar tokens etc on Ethereum mainnet.
The following functions makes use of ERC20's transferFrom() in following contracts:
1) In VouchFaucet.sol, the claimTokens() is called by users to claim the tokens and the token is transferred to user but the transfer return value is not checked and similarly in case of transferERC20() function.
```solidity
function claimTokens(address token, uint256 amount) external {
    require(claimedTokens[token][msg.sender] <= maxClaimable[token], "amount>max");

    @> IERC20(token).transfer(msg.sender, amount);
    transfer return value

    emit TokensClaimed(msg.sender, token, amount);
}

function transferERC20(address token, address to, uint256 amount) external onlyOwner {

    @> IERC20(token).transfer(to, amount);
    transfer return value

}
```
2) In ERC1155Voucher.transferERC20(), tokens are being transferred to recipient address and return value is not checked.
```solidity
function transferERC20(address token, address to, uint256 amount) external onlyOwner {

    @> IERC20(token).transfer(to, amount);
    transfer return value

}
```
The issue here is with the use of unsafe transfer() function. The ERC20.transfer() function return a boolean value indicating success. This parameter needs to be checked for success. Some tokens do not revert if the transfer failed but return false instead.
Some tokens like USDT don't correctly implement the EIP20 standard and their transfer() function return void instead of a success boolean. Calling these functions with the correct EIP20 function signatures will always revert.
Tokens that don't actually perform the transfer and return false are still counted as a correct transfer and tokens that don't correctly implement the latest EIP20 spec, like USDT, will be unusable in the protocol as they revert the transaction because of the missing return value. There could be silent failure in transfer which may lead to loss of user funds in ERC1155Voucher.transferERC20() and VouchFaucet.claimTokens()
Tokens that don't actually perform the transfer and return false are still counted as a correct transfer and tokens that don't correctly implement the latest EIP20 spec will be unusable in the protocol as they revert the transaction because of the missing return value. This will lead to loss of user funds.

## Recommendation
Use OpenZeppelin's SafeERC20 versions with the safeTransfer() function instead of transfer().
For example, consider below changes in VouchFaucet.sol:
```solidity
+ import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
contract VouchFaucet is Ownable {
+ using SafeERC20 for IERC20;
    function claimTokens(address token, uint256 amount) external {
        require(claimedTokens[token][msg.sender] <= maxClaimable[token], "amount>max");

        - IERC20(token).transfer(msg.sender, amount);
        + IERC20(token).safeTransfer(msg.sender, amount);
        emit TokensClaimed(msg.sender, token, amount);
    }

    function transferERC20(address token, address to, uint256 amount) external onlyOwner {

        - IERC20(token).transfer(to, amount);
        + IERC20(token).safeTransfer(to, amount);
    }
}
```

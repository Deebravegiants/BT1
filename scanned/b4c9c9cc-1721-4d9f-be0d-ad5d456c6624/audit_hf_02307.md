# [M] Improper Fee Handling Of Deposit

## Summary
Severity: Medium
Contest weight: 0.4053
Dataset id: 12571
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function depositETH() external payable nonReentrant {
    require(vaultParams.asset == WETH, "!WETH");
    require(msg.value > 0, "!value");
    _depositFor(msg.value, msg.sender);
    IWETH(WETH).deposit{value: msg.value}();
}

function deposit(uint256 amount) external nonReentrant {
    require(amount > 0, "!amount");
    _depositFor(amount, msg.sender);
    if (depositFee > 0){
        uint256 fee = amount.mul(depositFee).div(100 * Vault.FEE_MULTIPLIER);
        amount += fee;
        // An approve() by the msg.sender is required beforehand
        IERC20(vaultParams.asset).safeTransferFrom(
            msg.sender,
            address(this),
            amount
        );
    }
}
```
It comes to our attention that the depositFee is charged in the deposit() routine, but not in the depositETH() routine. This will cause inconsistency in the fee charging and a normal user could bypass the fee charging by calling the depositETH() routine.

## Recommendation
Revisit the above logic of depositETH() to handle the depositFee properly.

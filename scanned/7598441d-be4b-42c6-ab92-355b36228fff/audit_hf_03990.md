# [M] Bad debt liquidation doesn't allow liquidator

## Summary
Severity: Medium
Contest weight: 0.7474
Dataset id: 20367
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
More detailed scenario 1. Alice account goes into bad debt for whatever reason. For example, the account has 150 DAI borrowed, but only 100 DAI assets. 2. Bob tries to liquidate Alice account, but his transaction reverts, because remaining DAI liability after repaying 100 DAI assets Alice has, will be 50 DAI bad debt. liquidate code will try to call Bob's callee contract to swap 0.03 WETH to 50 DAI sending it 0.03 WETH. However, since Alice account has 0 WETH, the transfer will revert. 3. Bob tries to work around the liquidation problem: 3.1. Bob calls liquidate with strain set to type(uint256).max. Liquidation succeeds, but Bob doesn't receive anything for his liquidation (he receives 0 ETH bonus). Alice's ante is stuck in the contract until Alice bad debt is fully repaid. 3.2. Bob sends 0.03 WETH directly to Alice account and calls liquidate normally. It succeeds and Bob gets his bonus for liquidation (0.01 ETH). He has 0.02 ETH net loss from liquidation (in addition to gas fees). In both cases there is no incentive for Bob to liquidate Alice. So it's likely Alice account won't be liquidated and a borrow of 150 will be stuck in Alice account for a long time. Some lender depositors who can't withdraw might still have incentive to liquidate Alice to be able to withdraw from lender, but Alice's ante will still be stuck in the contract. Liquidators are not compensated for bad debt liquidations in some cases. Ante (liquidator bonus) is stuck in the borrower smart contract until bad debt is repaid. There is not enough incentive to liquidate such bad debt accounts, which can lead for these accounts to accumulate even bigger bad debt and lender depositors being unable to withdraw their funds from lender. Borrower.liquidate calculates remaining liabilities after assets are used to repay 
```solidity
// src/Borrower.sol#L231-L236
```
Notice, that if both assets are 0, liabilities0 or liabilities1 will still be non-0 if bad debt has happened. Since either liabilities0 or liabilities1 are non-0, shouldSwap is set to true:
```solidity
// src/Borrower.sol#L239-L250
// src/Borrower.sol#L263
// src/Borrower.sol#L273
```

## Proof of Concept
The scenario above is demonstrated in the test, add it to test/Liquidator.t.sol:
```solidity
function test_badDebtLiquidationAnte() public {
    // malicious user borrows at max leverage + some safety margin
    uint256 margin0 = 1e18;
    uint256 borrows0 = 100e18;
    deal(address(asset0), address(account), margin0);
    bytes memory data = abi.encode(Action.BORROW, borrows0, 0);
    account.modify(this, data, (1 << 32));
    // borrow increased by 50%
    _setInterest(lender0, 15000);
    emit log_named_uint("User borrow:", lender0.borrowBalance(address(account)));
    emit log_named_uint("User assets:", asset0.balanceOf(address(account)));
    // warn account
    account.warn((1 << 32));
    // skip warning time
    skip(LIQUIDATION_GRACE_PERIOD);
    lender0.accrueInterest();
    // liquidation reverts because it requires asset the account doesn't have to swap
    vm.expectRevert();
    account.liquidate(this, bytes(""), 1, (1 << 32));
    // liquidate with max strain to avoid revert when trying to swap assets account doesn't have
    account.liquidate(this, bytes(""), type(uint256).max, (1 << 32));
    emit log_named_uint("Liquidated User borrow:", lender0.borrowBalance(address(account)));
    emit log_named_uint("Liquidated User assets:", asset0.balanceOf(address(account)));
    emit log_named_uint("Liquidated User ante:", address(account).balance);
}
```
Execution console log:
User borrow:: 150000000000000000000
User assets:: 101000000000000000000
Liquidated User borrow:: 49000000162000000001
Liquidated User assets:: 0
Liquidated User ante:: 10000000000000001

## Recommendation
Consider verifying the bad debt situation and not forcing swap which will fail, so that liquidation can repay whatever assets account still has and give liquidator its full bonus.

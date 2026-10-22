# [H] claimCOMPAndTransfer() COMP may be locked

## Summary
Severity: High
Contest weight: 0.7727
Dataset id: 19992
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can keep front-run claimCOMPAndTransfer() to trigger COMPTROLLER.claimComp() first, causing netBalance in claimCOMPAndTransfer() to be 0 all the time, resulting in COMP not being transferred out and locked in the contract. claimCOMPAndTransfer() use for "Claims COMP incentives earned and transfers to the treasury manager contract". The code is as follows:
```solidity
function claimCOMPAndTransfer(address[] calldata cTokens)
    external
    override
    onlyManagerContract
    nonReentrant
    returns (uint256)
{
    uint256 balanceBefore = COMP.balanceOf(address(this));
    COMPTROLLER.claimComp(address(this), cTokens);
    uint256 balanceAfter = COMP.balanceOf(address(this));
    uint256 netBalance = balanceAfter.sub(balanceBefore);
    // transfer out `netBalance`
    if (netBalance > 0) {
        COMP.safeTransfer(msg.sender, netBalance);
    }
    return netBalance;
}
```
From the above code, we can see that this method only turns out the difference value netBalance. But COMPTROLLER.claimComp() can be called by anyone, if there is a malicious user front-run this transaction to triggers COMPTROLLER.claimComp() first, this will cause thenetBalance to be 0 all the time, resulting in COMP not being transferred out and being locked in the contract. The following code is from Comptroller.sol https://github.com/compound-finance/compound-protocol/blob/master/contracts/Comptroller.sol
```solidity
function claimComp(address holder, CToken[] memory cTokens) public {
    // anyone can call it
    address[] memory holders = new address[](1);
    holders[0] = holder;
    claimComp(holders, cTokens, true, true);
}
```
COMP may be locked into the contract

## Recommendation
Transfer all balances, not using netBalance

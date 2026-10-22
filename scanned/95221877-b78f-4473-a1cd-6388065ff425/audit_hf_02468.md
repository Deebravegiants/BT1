# [M] Arbitrage on `stake

## Summary
Severity: Medium
Contest weight: 0.4693
Dataset id: 13225
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Issue: there is a huge arb opportunity for people who deposit 1 block before the `rebase()`.

Consequences: then they can call `instantUnstakeReserve` or `instantUnstakeCurve` to unstake the staked amount, in this way the profit that needs to be distributed on the next rebase increases, he also messes up the rewards for the other holders as the `instantUnstakeReserve` does not burn the `YIELD_TOKEN`. Even if there is a fee on the `instantUnstakeReserve`, there is still a chance for profit.

**Affected Code**
```solidity
function stake(uint256 _amount, address _recipient) public { // @audit-info [HIGH] 
    // if override staking, then don't allow stake
    require(!isStakingPaused, "Staking is paused");
    // amount must be non zero
    require(_amount > 0, "Must have valid amount");

    uint256 yieldyTotalSupply = IYieldy(YIELDY_TOKEN).totalSupply();

    // Don't rebase unless tokens are already staked or could get locked out of staking
    if (yieldyTotalSupply > 0) {
        rebase();
    }

    IERC20Upgradeable(STAKING_TOKEN).safeTransferFrom(
        msg.sender,
        address(this),
        _amount
    );

    Claim storage info = warmUpInfo[_recipient];

    // if claim is available then auto claim tokens
    if (_isClaimAvailable(_recipient)) {
        claim(_recipient);
    }

    _depositToTokemak(_amount);

    // skip adding to warmup contract if period is 0
    if (warmUpPeriod == 0) {
        IYieldy(YIELDY_TOKEN).mint(_recipient, _amount);
    } else {
        // create a claim and mint tokens so a user can claim them once warm up has passed
        warmUpInfo[_recipient] = Claim({
            amount: info.amount + _amount,
            credits: info.credits +
                IYieldy(YIELDY_TOKEN).creditsForTokenBalance(_amount),
            expiry: epoch.number + warmUpPeriod
        });

        IYieldy(YIELDY_TOKEN).mint(address(this), _amount);
    }

    sendWithdrawalRequests();
}
```

## Recommendation
Burn the `YIELD_TOKEN` amount in the `instantUnstakeReserve`.

Yes, the fee on instant Unstake needs to be set high enough to make this not profitable. 

If a curve pool exists, then this does become possible to arb the rebase and something that should be fixed, potentially with not allowing the warm up period to be violated for instant unstaking (through curve at the very least). 

I would qualify this as Medium severity, and leaking value. 

`2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.`

I took another look, medium seems reasonable too.

# [H] `Staking.sol#stake`

## Summary
Severity: High
Contest weight: 0.5656
Dataset id: 13086
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
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
```

`Staking.sol#stake()` is a public function and you can specify an arbitrary address as the `_recipient`.

When `warmUpPeriod > 0`, with as little as 1 wei of `YIELDY_TOKEN`, the `_recipient`’s `warmUpInfo` will be push back til `epoch.number + warmUpPeriod`.

## Recommendation
Consider changing to not allow deposit to another address when `warmUpPeriod > 0`.

Should be high right? Funds are locked. See <https://github.com/code-423n4/2022-06-yieldy-findings/issues/245#issuecomment-1167616593>

Agree this should be high. The cost of the attack is negligible and could cause basic perpetual grievance on all users with one simple script.

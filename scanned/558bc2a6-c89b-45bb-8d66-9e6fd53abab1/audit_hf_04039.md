# [H] Can steal gOhm by calling

## Summary
Severity: High
Contest weight: 0.7857
Dataset id: 20471
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
1. Alice creates a Cooler. 9 times, she calls requestLoan (not through the Clearinghouse) to request a loan of 0.000001 DAI collateralized by 2 gOhm. For each loan, she then calls clearLoan and loans the 0.000001 DAI to herself.
2. One week later, Bob calls Clearinghouse.lendToCooler and takes a loan for 3000 DAI collateralized by 1 gOHM
3. Alice defaults on the loans she made to herself and waits 7 days
4. Bob defaults on his loan
5. Alice calls Clearinghouse.claimDefaulted, passing in both her loans to herself and Bob's loan from the Clearinghouse. Clearinghouse.claimDefaulted calls Cooler.claimDefaulted on each, returning 18 gOhm to Alice and 1 gOhm to the Clearinghouse.
6. For each of Alice's loan, the keeper reward is incremented by the max award of 0.1 gOhm. For Bob's loan, the keeper reward is incremented by somewhere between 0 and 0.05 gOhm, depending on how much time has elapsed since Bob's loan defaulted.
7. The keeper reward is transferred to Alice. Alice's reward will be between 0.9 and 0.95 gOhm, but it should be between 0 and 0.05 gOhm. The contract should recover between 0.95 and 1 gOhm, but it only recovers between 0.05 and 0.1 gOhm. Alice has effectively stolen 0.9 gOhm from the contract. can get this even without waiting 7 days from loan expiry time. It further requires the Clearinghouse have some extra gOhm around, as it will burn totalCollateral - keeperRewards. This can happen if the treasury or someone sends it some gOhm for some reason, or by calling claimDefault as in #3 . However, #5 extends this attack so that Alice can steal 100% of the collateral, even if the Clearinghouse has no extra gOhm lying around. loan duration to 0 seconds. So this only requires setting up 1 block in advance. Anyone can steal collateral from defaulted loans. ouse.sol#L191 Notice the lack of any checks that the loan's lender is the Clearingouse

```solidity
function claimDefaulted(address[] calldata coolers_, uint256[] calldata loans_)
    external
{
    uint256 loans = loans_.length;
    if (loans != coolers_.length) revert LengthDiscrepancy();
    uint256 totalDebt;
    uint256 totalInterest;
    uint256 totalCollateral;
    uint256 keeperRewards;
    for (uint256 i=0; i < loans;) {
        // Validate that cooler was deployed by the trusted factory.
        if (!factory.created(coolers_[i])) revert OnlyFromFactory();
        // Claim defaults and update cached metrics.
        (uint256 debt, uint256 collateral, uint256 elapsed) = Cooler(coolers_[i]).claimDefaulted(loans_[i]);
        // Cap rewards to 5% of the collateral to avoid OHM holder's dillution.
        uint256 maxAuctionReward = collateral * 5e16 / 1e18;
        // Cap rewards to avoid exorbitant amounts.
        uint256 maxReward = (maxAuctionReward < MAX_REWARD) ? maxAuctionReward : MAX_REWARD;
        // Calculate rewards based on the elapsed time since default.
        keeperRewards = (elapsed < 7 days) ? keeperRewards + maxReward * elapsed / 7 days : keeperRewards + maxReward;
    }
}
```

#L318 Cooler.claimDefaulted can be called by anyone.
```solidity
function claimDefaulted(uint256 loanID_) external returns (uint256, uint256, uint256) {
    Loan memory loan = loans[loanID_];
    delete loans[loanID_];
    // Hey look, no checks on sender
}
```

## Recommendation
Check that the Clearinghouse is the originator of all loans passed to claimDefaulted

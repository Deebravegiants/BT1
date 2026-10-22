# [H] Double Minting of Janis Reward in JanisMinter

## Summary
Severity: High
Contest weight: 0.6132
Dataset id: 12323
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the token issuance and management, the JanisDex protocol has a JanisMinter contract, which is the sole entity to have the privilege to mint new JanisToken. While reviewing various scenarios for token issuance, we notice a speciﬁc routine has a ﬂawed implementation. To elaborate, we show below the related mintReferralsOnly() function. It implements a rather straightforward logic in minting the commission to the referrer as well as the reward to the referee, i.e., the user. It comes to our attention the user reward is incorrectly minted as it mints the _minting amount (line 135) one more time!
```solidity
function mintReferralsOnly(address _user, uint _minting) public onlyOperator {
    uint commission = _minting * referralBonusE4 / 1e4;
    uint reward = _minting * refereeBonusE4 / 1e4;
    address referrer = referrers[_user];
    if (referrer != address(0) && _user != address(0) && commission > 0) {
        totalReferralCommission[referrer] += commission;
        totalReferralCommissionPerUser[referrer][_user] += commission;
        JanisToken.mint(referrer, commission);
        emit JanisMinted(referrer, commission);
        emit ReferralCommissionRecorded(referrer, _user, commission);
    }
    if (_user != address(0) && referrer != address(0) && reward > 0) {
        JanisToken.mint(_user, _minting);
        totalRefereeReward[_user] += reward;
        totalRefereeRewardPerReferrer[_user][referrer] += reward;
        JanisToken.mint(_user, reward);
        emit JanisMinted(_user, reward);
        emit ReferralCommissionRecorded(_user, referrer, reward);
    }
}
```

## Recommendation
Revise the above routine to ensure only commission and reward are minted.

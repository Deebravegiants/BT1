# [H] Referrer can get less referral reward due to

## Summary
Severity: High
Contest weight: 0.3761
Dataset id: 23035
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Referrers can get 5% extra BORING token for their referral, however a trader's referrer info can be overwritten in onFlowChanged, and cause original referrer to lose rewards.
In onFlowChanged, if there is a previous flow record for trader, userData.distributor and userData.referrer will be set to previous ones:
if (prevFlowRate > 0) {
    userData = InFlowUserData({
        distributor: DistributionFeeDIP.getCurrentDistributor(ITorex(msg.sender), trader),
        referrer: QuadraticEmissionTIP.getCurrentReferrer(ITorex(msg.sender), trader)
    });
}
And this userData.referrer is used somewhere else later, to get the SleepPod of such address:
userData.referrer = address(InitialStakingTIP.getOrCreateSleepPod(sleepPodBeacon, userData.referrer));
The logic for getOrCreateSleepPod is to create a pod for address, if the address has no pod registered in storaged. After this, at the end of the function, emission info is updated:
QuadraticEmissionTIP.onInFlowChanged(emissionTreasury, ITorex(msg.sender), trader, userData.referrer, prevFlowRate, newFlowRate);
And in this function, we see:
if (oldRefData.referrer == referrer) { // this branch is a small optimization
    // invariant: oldRefData.referrer != referrer != address(0)
    emissionTreasury.updateMemberEmissionUnits(address(torex), referrer, emissionPool.getUnits(referrer) + newReferralUnits - oldRefData.referrerUnits);
} else {
    if (referrer != address(0)) {
        emissionTreasury.updateMemberEmissionUnits(address(torex), referrer, emissionPool.getUnits(referrer) + newReferralUnits);
    }
    if (oldRefData.referrer != address(0)) {
        emissionTreasury.updateMemberEmissionUnits(address(torex), oldRefData.referrer, emissionPool.getUnits(oldRefData.referrer) - oldRefData.referrerUnits);
    }
}
$.referrals[torex][trader] = ReferralData(referrer, toUint96(newReferralUnits));
emit ReferrerUpdated(torex, trader, newTraderUnits, referrer, newReferralUnits);
}
}
Which compares the referrer to the old one, and updates the record eventually.
Let's assume Bob, who created a flow for the first time, and set Alice as his referrer, as his prevFlow is 0, this will not fetch his existing referrer and distributor info.
Continue down the function, a pod for both Bob and Alice will be created, assuming both of them are new to the protocol.
Then, emission will be updated, where the trader will be Bob's pod address, while referrer will be Alice's pod address. This is all good, until Bob made a change to the flow, and triggers onFlowChanged again. Now, as Bob has a previous flow in record, userData.referrer will be set to his existing referrer address, which is Alice's pod address, this makes sense, as Alice's rewards are sent to her pod.
However, a few lines later into the function, when getting pod for Bob and his referrer, Bob's pod will be correctly fetched, but not referrer's. Because userData.referrer, which is used for getting pod, is actually a pod itself. Since there is no way a pod to have its own pod, a new pod will be created, and returned for the function.
Now, Alice's pod's pod will be userData.referrer, and passed into updating emission units, makes this address the new referrer, until next time Bob makes some change, this pod's address will be fetched for referrer, and when getting pod for this address, it will be none, as this address is also a pod, so a new pod will be created for it, and the cycle continues.
Original referrer will get less BORING reward.
if (prevFlowRate > 0) {
    userData = InFlowUserData({
        distributor: DistributionFeeDIP.getCurrentDistributor(ITorex(msg.sender), trader),
        referrer: QuadraticEmissionTIP.getCurrentReferrer(ITorex(msg.sender), trader)
    });
}

## Recommendation
Move the else branch down to the pod address part, as the referrer will be a pod's address already.

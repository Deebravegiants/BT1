# [H] Incorrect accounting of cost share requests

## Summary
Severity: High
Contest weight: 0.6358
Dataset id: 22755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect accounting of cost share requests leading to loss of funds for users and putting the entire protocol at risk. The issue lies in the createCostshareRequest function where in the CostShareRequest struct, requestPayout is recorded, but then in the incrementCounts and setAvailableBenefits functions, claimAmount is passed. The value of requestPayout is 10% lower than that of claimAmount, with the idea being that in case of an incident, the user bears 10% of the losses, and the rest are covered by the protocol. The setAvailableBenefits function decreases/increases the value of availableCostShareBenefits for the respective membership. Due to the inconsistent use of claimAmount/requestPayout, the user loses 10% of the availableCostShareBenefits they have paid for, even when the claim is denied. The incrementCounts function increases the value of openPWPRequestAmount, an important variable used in calculating fShare and the price of FSD. When a claim is finalized, the decrementCounts function is called, which should decrease the value of openPWPRequestAmount by the same value it was increased when the claim was opened. However, this does not happen, and only 90% of the added value is subtracted. Thus, openPWPRequestAmount constantly has a non-zero value even if there are no open requests at the moment. Over time, this value will accumulate and more and more ether will be needed to maintain a ratio > 1. Also openCostShareBenefits will also store wrong values.
```solidity
//Modified test from fsdClaims.test.ts
it("should allow admin to deny a claim", async () => {
    const [frank] = accounts.slice(4, 5);
    //purchase membership of 100 ETH
    await fairSideNetwork.connect(frank).purchaseMembership(ethToWei("10"), coverAddress, { value: ethToWei("10") });

    await increaseMonths(6);
    //frank purchases 100 ETH of fsd to cover assessors fee
    await fsd.connect(frank).bond(0, {
        value: ethToWei("10"),
    });
    // this returns a list of all memberships for address, since we only have one membership, we select index 0

    const [cover] = await fairSideNetwork.getAccountMembership(frank.address);
    const frankCoverID = cover.toNumber();
    let frankMembership = await fairSideNetwork.membership(frankCoverID);
    expect(frankMembership.availableCostShareBenefits).equal(ethToWei("10"));
    // frank tries to file a claim without approving fsd
    await expect(fairSideClaims.connect(frank).openPWPRequest(ethToWei("5"), frankCoverID, false)).to.be.revertedWith(
    );
    // frank tries to pay for ETH, but assuming he doesn't have enough eth for fee, and sends 0

    await expect(
        fairSideClaims.connect(frank).openPWPRequest(ethToWei("5"), frankCoverID, true, { value: 0 })
    // frank gives approval
    await fsd.connect(frank).approve(fairSideClaims.address, ethToWei("10000"));
    // frank tries to open a CSR for more eth than he has covered
    await expect(
        fairSideClaims.connect(frank).openPWPRequest(ethToWei("15"), frankCoverID, false)
    ).to.be.revertedWith("FSClaims_CostRequestExceedsAvailableCostShareBenefits()");
    // frank opens a CSR
    const openPWPtx = await fairSideClaims.connect(frank).openPWPRequest(ethToWei("5"), frankCoverID, false);
    const receipt = await openPWPtx.wait(1);
    // Get the last event, thats where the CreateCSR event was emitted
    const res = receipt.events.at(-1);
    const claimId = res.args.id.toNumber();
    let getClaim = await fairSideClaims.costShareRequests(frankCoverID);
    expect(getClaim.status).equal(ClaimStatus.IN_PROGRESS);
    console.log("Amount ", getClaim.claimAmount );
    frankMembership = await fairSideNetwork.membership(frankCoverID);
    expect(frankMembership.availableCostShareBenefits).equal(ethToWei("5"));
    // we had PWP & Global claims that would have been depicted by the csrType with values of integer 1, 2
    // since that idea is deprecated, but we still maintained the parameter, we default it to 0

    const csrType = 0;
    const reason = Buffer.from(approveClaimReason, "utf8");
    const blockTimestamp = await getCurrentBlockTimestamp();
    let openRequestsBefore = await fairSideClaims.totalOpenRequests();
    console.log("Open requests before seedPWPVerdictTx: ", openRequestsBefore);
    // guardian seeds pwp claim information
    const seedPWPVerdictTx = await fairSideClaims
        .connect(owner)
        .seedPWPVerdict(claimId, Action.DENY_CLAIM, csrType, reason);
    const receiptSeed = await seedPWPVerdictTx.wait(1);
    const emittedEvent = receiptSeed.events.at(-1);
    expect(emittedEvent.event).equal("DenyCSR");
    expect(emittedEvent.args.id).equal(claimId);
    expect(emittedEvent.args.csrType).equal(csrType);
    expect(emittedEvent.args.assessor).equal(owner.address);
    expect(emittedEvent.args.reason).equal(`0x${reason.toString("hex")}`);
    expect(Number(emittedEvent.args.timestamp)).closeTo(blockTimestamp, 10);
    getClaim = await fairSideClaims.costShareRequests(claimId);
    expect(getClaim.status).equal(ClaimStatus.DENIED);
    frankMembership = await fairSideNetwork.membership(frankCoverID);
    console.log("Available csb (should be 10 ethers): ", frankMembership.availableCostShareBenefits);
    let openRequestsAfter = await fairSideClaims.totalOpenRequests();
    console.log("Open requests after (should be 0): ", openRequestsAfter);
    // one year later, frank tries to file a claim again with expired membership
    await increaseYears(1);
    // frank gives approval
    await fsd.connect(frank).approve(fairSideClaims.address, ethToWei("10000"));
    // frank open a CSR
    await expect(fairSideClaims.connect(frank).openPWPRequest(ethToWei("5"), frankCoverID, false)).to.be.revertedWith(
        "FSClaims_GracePeriodPassed()"
    );
});
```
Loss of funds for users due to loss of already paid CSB. Significant impact on the protocol's operation, limiting the ability to create memberships and leading to losses. Possibility of DOS, intentional or not.

## Recommendation
Update openCostShareBenefits() to use requestPayout instead of claimAmount.

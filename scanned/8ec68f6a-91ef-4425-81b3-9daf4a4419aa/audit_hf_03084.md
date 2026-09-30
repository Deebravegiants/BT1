# [M] Validators will be unable to validate current round after priceFeed.transmit() fails

## Summary
Severity: Medium
Contest weight: 0.3719
Dataset id: 17408
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Validators used for the current round cannot submit for the same round should the transmission fail. Should transmission fail, the transaction will not revert, but an error log is emitted. This means that the validators’ last signed round will still be updated to the latest round, but price feed’s latestAggregatorRoundId remains unchanged. Existing validators who participated in the failed update will then be unable to participate in the current round because of the condition require(fluxPriceFeeds[id].lastSignedRound[recoveredSigner] < _roundId, "Duplicate signature"); A new, mutually exclusive, set of validators is required to sign the current round.

## Proof of Concept
The current implementation of `priceFeed.transmit()` will revert under the following circumstances:
- Caller does not have `VALIDATOR_ROLE`
- `latestAggregatorRoundId` increment overflows
- Insufficient gas remaining
Of the 3 cases, the first would be the most probable, as demonstrated in the test script below.
it.only("will have providers be unable to sign current round after failed transmission", async function () {
    // step 0: setup
    const pricePair = this.eth_usd_str;
    const decimals = 3;
    let answers = [3000, 4000];
    // deploy oracle
    await this.proxy
        .connect(this.signers.admin)
        .deployOracle(this.eth_usd_str, decimals, [this.provider1.address, this.provider2.address]);
    const PriceFeedContract = await ethers.getContractFactory("FluxPriceFeed");
    const eth_usd_addr = await this.proxy.connect(this.signers.admin).addressOfPricePair(this.eth_usd_id);
    const pricefeed = PriceFeedContract.attach(eth_usd_addr);
    const VALIDATOR_ROLE = keccak256(ethers.utils.toUtf8Bytes("VALIDATOR_ROLE"));
    // transfer price feed owner to admin
    await this.proxy.connect(this.signers.admin).transferOwner(this.eth_usd_id, this.signers.admin.address);
    // increment price feed round by successfully transmitting an answer
    // so that duplicate signature will be checked
    await pricefeed.connect(this.signers.admin).grantRole(VALIDATOR_ROLE, this.signers.admin.address);
    await pricefeed.connect(this.signers.admin).transmit(1);
    let round = await this.proxy.latestRoundOfPricePair(this.eth_usd_id);
    // sign answer 0 by provider1 and answer 1 by provider2
    let p1_msgHash = ethers.utils.solidityKeccak256(["string", "uint8", "uint32", "int192"], [pricePair, decimals, round, answers[0]]);
    let p2_msgHash = ethers.utils.solidityKeccak256(["string", "uint8", "uint32", "int192"], [pricePair, decimals, round, answers[1]]);
    let p1_sig = await this.provider1.signMessage(arrayify(p1_msgHash));
    let p2_sig = await this.provider2.signMessage(arrayify(p2_msgHash));
    let sigs = [p1_sig, p2_sig];
    // step 1: revoke proxy's VALIDATOR_ROLE from price feed
    await pricefeed.connect(this.signers.admin).revokeRole(VALIDATOR_ROLE, this.proxy.address);
    // step 2: attempt transmission, will not revert but price feed would not have updated
    await this.proxy.connect(this.signers.admin).transmit(sigs, pricePair, decimals, round, answers);
    // same round
    expect(await this.proxy.latestRoundOfPricePair(this.eth_usd_id)).to.be.eq(round);
    // step 3: re-grant proxy VALIDATOR_ROLE, re-attempt transmission
    // will revert
    await pricefeed.connect(this.signers.admin).grantRole(VALIDATOR_ROLE, this.proxy.address);
    await expect(this.proxy.connect(this.signers.admin).transmit(sigs, pricePair, decimals, round, answers)).to.be.revertedWith("Duplicate signature");
});

## Recommendation
We suggest making `priceFeed.transmit()` callable by the factory only. Then, the try-catch block can be removed. Replaying failed transactions wouldn’t be a concern if data freshness is checked, as suggested in the recommendation for H-01.

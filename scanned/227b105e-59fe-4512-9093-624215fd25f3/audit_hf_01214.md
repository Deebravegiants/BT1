# [H] `Minter.sol#startInflation`

## Summary
Severity: High
Contest weight: 0.7909
Dataset id: 5409
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function startInflation() external override onlyGovernance {
    require(lastEvent == 0, "Inflation has already started.");
    lastEvent = block.timestamp;
    lastInflationDecay = block.timestamp;
}
```

As `lastEvent` and `lastInflationDecay` are not initialized in the `constructor()`, they will remain to the default value of `0`.

However, the permissionless `executeInflationRateUpdate()` method does not check the value of `lastEvent` and `lastInflationDecay` and used them directly.

As a result, if `executeInflationRateUpdate()` is called before `startInflation()`:

  1. L190, the check of if `_INFLATION_DECAY_PERIOD` has passed since `lastInflationDecay` will be `true`, and `initialPeriodEnded` will be set to `true` right away;
  2. L188, since the `lastEvent` in `totalAvailableToNow += (currentTotalInflation * (block.timestamp - lastEvent));` is `0`, the `totalAvailableToNow` will be set to `totalAvailableToNow ≈ currentTotalInflation * 52 years`, which renders the constrains of `totalAvailableToNow` incorrect and useless.

```solidity
        function executeInflationRateUpdate() external override returns (bool) {
            return _executeInflationRateUpdate();
        }

        function _executeInflationRateUpdate() internal returns (bool) {
            totalAvailableToNow += (currentTotalInflation * (block.timestamp - lastEvent));
            lastEvent = block.timestamp;
            if (block.timestamp >= lastInflationDecay + _INFLATION_DECAY_PERIOD) {
                currentInflationAmountLp = currentInflationAmountLp.scaledMul(annualInflationDecayLp);
                if (initialPeriodEnded) {
                    currentInflationAmountKeeper = currentInflationAmountKeeper.scaledMul(
                        annualInflationDecayKeeper
                    );
                    currentInflationAmountAmm = currentInflationAmountAmm.scaledMul(
                        annualInflationDecayAmm
                    );
                } else {
                    currentInflationAmountKeeper =
                        initialAnnualInflationRateKeeper /
                        _INFLATION_DECAY_PERIOD;

                    currentInflationAmountAmm = initialAnnualInflationRateAmm / _INFLATION_DECAY_PERIOD;
                    initialPeriodEnded = true;
                }
                currentTotalInflation =
                    currentInflationAmountLp +
                    currentInflationAmountKeeper +
                    currentInflationAmountAmm;
                controller.inflationManager().checkpointAllGauges();
                lastInflationDecay = block.timestamp;
            }
            return true;
        }

        // Used for final safety check to ensure inflation is not exceeded
        uint256 public totalAvailableToNow;

        function _mint(address beneficiary, uint256 amount) internal returns (bool) {
            totalAvailableToNow += ((block.timestamp - lastEvent) * currentTotalInflation);
            uint256 newTotalMintedToNow = totalMintedToNow + amount;
            require(newTotalMintedToNow <= totalAvailableToNow, "Mintable amount exceeded");
            totalMintedToNow = newTotalMintedToNow;
            lastEvent = block.timestamp;
            token.mint(beneficiary, amount);
            _executeInflationRateUpdate();
            emit TokensMinted(beneficiary, amount);
            return true;
        }
```

## Recommendation
Consider initializing `lastEvent`, `lastInflationDecay` in `constructor()`.

or

Consider adding `require(lastEvent != 0 && lastInflationDecay != 0, "...")` to `executeInflationRateUpdate()`.

The warden has shown how `startInflation` can be bypassed, breaking the Access Control as well as the Sponsor Goal for Emissions.

Because of this I believe High Severity to be appropriate.

The sponsor has mitigated in a subsequent PR

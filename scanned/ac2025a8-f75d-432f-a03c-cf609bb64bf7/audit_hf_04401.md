# [M] `PoolV3#repayCreditAccount

## Summary
Severity: Medium
Contest weight: 0.3351
Dataset id: 21734
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the profit and loss accounting performed by the PoolV3 contract when a credit manager calls repayCreditAccount. The function is supposed to mint lpETH shares to the treasury when a repayment yields profit, or burn shares from the treasury when a loss occurs. However, the implementation mistakenly uses the public convertToShares() helper, which calculates shares based on the ERC4626 exchange rate derived from total assets and total supply, instead of the internal _convertToShares() helper that enforces the pool’s 1:1 WETH‑to‑lpETH rate. Because the pool is designed to treat WETH and lpETH as having a one‑to‑one relationship, using convertToShares() can return a smaller number of shares than the actual amount of profit or loss. Consequently, when profit > 0 the treasury receives fewer lpETH shares than it should, and when loss > 0 the treasury may burn fewer shares than required, leaving an excess balance. This mis‑calculation can be triggered by any credit manager during a normal repayment flow, making it exploitable without special permissions. An attacker can repeatedly generate profit‑bearing repayments, causing the treasury to be under‑minted each time and effectively siphoning value to the attacker’s account. The impact is an incorrect treasury profit balance, which translates to missing or reduced profit distribution for users and a breach of the protocol’s accounting guarantees. The issue manifests only during the repayCreditAccount call when profit or loss is non‑zero, and it affects the treasury, lenders, and any participants relying on accurate profit accounting. It was discovered during a manual audit by Code4rena, where the auditor noticed that the conversion used in deposit (which is 1:1) differed from the conversion used in repayment. The bug is subtle because both functions return a uint256 and appear interchangeable, so tests that only check for successful execution may not reveal the discrepancy. To remediate, the contract should replace every call to convertToShares() inside repayCreditAccount with the internal _convertToShares() function, thereby aligning the share calculation with the pool’s defined exchange rate and restoring correct profit and loss accounting. This class of bug is an accounting mismatch caused by inconsistent conversion logic, similar to rounding or unit‑conversion errors that break financial invariants. From a user’s perspective the symptoms are that after a profitable repayment the treasury’s lpETH balance grows less than expected, profit payouts appear lower, or after a loss the treasury retains extra lpETH, leading to confusing UI numbers such as “profit received: 0” or “treasury balance unchanged despite loss”.

## Proof of Concept
Anyone can deposit `WETH` for `lpETH` by calling `PoolV3#deposit()` or `PoolV3#mint()`. The exchange rate of `WETH:lpETH` is `1:1`. The eligible credit manager can borrow `WETH` by calling `PoolV3#lendCreditAccount()`, and repay the debt and profit lately by calling `PoolV3#repayCreditAccount()`. The corresponding amount of `lpETH` will be minted to `treasury` if there is profit, and the corresponding amount of `lpETH` should be burned from `treasury` if there is any loss:
    
            if (profit > 0) {
    @>          _mint(treasury, convertToShares(profit)); // U:[LP-14B]
            } else if (loss > 0) {
                address treasury_ = treasury;
                uint256 sharesInTreasury = balanceOf(treasury_);
    @>          uint256 sharesToBurn = convertToShares(loss);
                if (sharesToBurn > sharesInTreasury) {
                    unchecked {
                        emit IncurUncoveredLoss({
                            creditManager: msg.sender,
                            loss: convertToAssets(sharesToBurn - sharesInTreasury)
                        }); // U:[LP-14D]
                    }
                    sharesToBurn = sharesInTreasury;
                }
                _burn(treasury_, sharesToBurn); // U:[LP-14C,14D]
            }

However, `convertToShares()` is used to calculate shares for profit and loss, while `_convertToShares()` is used to calculate shares in [`PoolV3#deposit()`](https://github.com/code-423n4/2024-07-loopfi/blob/main/src/PoolV3.sol#L243). `convertToShares()` uses the exchange rate of `E4626` to calculate shares instead of `1:1` exchange rate defined in `PoolV3`.

The incorrect `convertToShares()` call could highly return less shares than expected, resulting in the treasury owning incorrect balance.

## Recommendation
Use `_convertToShares()` for share calculation:
    
            if (profit > 0) {
    -           _mint(treasury, convertToShares(profit)); // U:[LP-14B]
    +           _mint(treasury, _convertToShares(profit)); 
            } else if (loss > 0) {
                address treasury_ = treasury;
                uint256 sharesInTreasury = balanceOf(treasury_);
    -           uint256 sharesToBurn = convertToShares(loss);
    +           uint256 sharesToBurn = _convertToShares(loss);
                if (sharesToBurn > sharesInTreasury) {
                    unchecked {
                        emit IncurUncoveredLoss({
                            creditManager: msg.sender,
                            loss: convertToAssets(sharesToBurn - sharesInTreasury)
                        }); // U:[LP-14D]
                    }
                    sharesToBurn = sharesInTreasury;
                }
                _burn(treasury_, sharesToBurn); // U:[LP-14C,14D]
            }

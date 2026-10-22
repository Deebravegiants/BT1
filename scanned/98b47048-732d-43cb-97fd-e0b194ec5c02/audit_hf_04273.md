# [M] Vault can be DoS

## Summary
Severity: Medium
Contest weight: 0.3406
Dataset id: 21332
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service condition in the vault’s share‑minting logic caused by an incorrect zero‑check in the internal conversion routine that translates deposited assets into vault shares. The function responsible for this conversion, often called toBase, only verifies whether the elastic component of the vault’s accounting structure (the total amount of underlying assets) is zero. It does not also verify that the base component, which represents the total supply of vault shares, is non‑zero. When the vault is freshly deployed its totalSupply (base) is zero. If an attacker makes a tiny deposit – for example 1 wei of the underlying token – the conversion routine sees a non‑zero elastic value, takes the else branch, and computes the number of shares as (elastic * total.base) / total.elastic. Because total.base is zero, the result is always zero, regardless of the deposited amount. Consequently the contract mints zero shares to the depositor, emits a Deposit event that appears normal, but the user receives no ownership tokens and the vault’s totalSupply remains zero. From that point onward any subsequent deposit will also be converted to zero shares, effectively locking the vault and preventing legitimate users from depositing or withdrawing assets. The attack does not directly steal funds; the assets remain in the vault, but the protocol becomes unusable, violating the business assumption that every deposit yields a positive share balance. This issue was discovered during a formal audit when the auditors examined the toBase implementation and noticed the missing check for total.base. It can be hard to notice because the transaction does not revert and the event logs look successful, so users may think their deposit succeeded while their balance stays at zero. The fix is to extend the zero‑condition to include both components of the accounting pair – i.e., treat the situation as a zero‑state when either total.elastic or total.base is zero – ensuring that a deposit in a zero‑supply vault yields a one‑to‑one share allocation instead of zero. This change restores the invariant that a non‑zero deposit always results in a non‑zero share amount, preventing the denial‑of‑service scenario.

## Proof of Concept
The `toBase` function only determines whether `total.elastic(_totalAssets)` is 0, not whether `totalSupply` is 0.
    
        function toBase(Rebase memory total, uint256 elastic,bool roundUp
        ) internal pure returns (uint256 base) {
    @       if (total.elastic == 0) {
                base = elastic;
            } else {
                //total.base = totalSupply ; total.elastic = _totalAssets
                base = (elastic * total.base) / total.elastic;
                if (roundUp && (base * total.elastic) / total.base < elastic) {
                    base++;
                }
            }
        }

When `totalSupply=0`, if `_totalAssets > 0`, `toBase` always returns 0.

An attacker can make a donation of `_totalAssets > 0`, the `toBase` function will then compute base through a branch in the else statement, since `totalSupply=0`. `base = 0 * elastic / total.elastic = 0`,

As a result, the number of deposit shares is always 0, and the protocol will not work.
    
        function deposit(address receiver) ....{
            .....
            shares = total.toBase(amount, false);
            _mint(receiver, shares);
            emit Deposit(msg.sender, receiver, msg.value, shares);
        }

An attacker can send Collateral token to the `StrategyAAVEv3(address(this))` contract,

`_totalAssets = collateralBalance - debtBalance`
    
        function _getMMPosition() internal virtual override view returns ( uint256 collateralBalance, uint256 debtBalance ) {
            DataTypes.ReserveData memory wethReserve = (aaveV3().getReserveData(wETHA()));
            DataTypes.ReserveData memory colleteralReserve = (aaveV3().getReserveData(ierc20A()));
            debtBalance = IERC20(wethReserve.variableDebtTokenAddress).balanceOf(address(this));
            collateralBalance = IERC20(colleteralReserve.aTokenAddress).balanceOf(address(this));
        }

## Recommendation
function toBase(Rebase memory total, uint256 elastic,bool roundUp
        ) internal pure returns (uint256 base) {
    -        if (total.elastic == 0) {
    +        if (total.elastic == 0 || total.base == 0) {
                base = elastic;
            } else {
                //total.base = totalSupply ; total.elastic = _totalAssets
                base = (elastic * total.base) / total.elastic;
                if (roundUp && (base * total.elastic) / total.base < elastic) {
                    base++;
                }
            }
        }

Thinking about this more, continuous DoS of vault deployment only lasts until it is fixed and does not seem to have any impact on user funds. Downgrading to `medium` severity.

Fixed → <https://github.com/baker-fi/bakerfi-contracts/pull/44>

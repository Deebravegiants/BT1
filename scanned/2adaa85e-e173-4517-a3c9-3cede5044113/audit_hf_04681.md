# [M] Vault Inflation Attack

## Summary
Severity: Medium
Contest weight: 0.5989
Dataset id: 22434
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can perform an inflation attack against the vault to steal the assets of the victim.
A malicious user can perform a donation to execute a classic first depositor/ERC4626 inflation Attack against the FlatCoin vault. The general process of this attack is well-known, and a detailed explanation of this attack can be found in many of the resources such as the following:
• https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks
• https://mixbytes.io/blog/overview-of-the-inflation-attack
In short, to kick-start the attack, the malicious user will often usually mint the smallest possible amount of shares (e.g., 1 wei) and then donate significant assets to the vault to inflate the number of assets per share. Subsequently, it will cause a rounding error when other users deposit.
However, in Flatcoin, there are various safeguards in place to mitigate this attack. Thus, one would need to perform additional steps to workaround/bypass the existing controls.
Let's divide the setup of the attack into two main parts:
1. Malicious user mint 1 mint of share
2. Donate or transfer assets to the vault to inflate the assets per share
Part 1 - Malicious user mint 1 mint of share
Users could attempt to mint 1 wei of share. However, the validation check at Line 79 will revert as the share minted is less than MIN_LIQUIDITY = 10_000. However, this minimum liquidation requirement check can be bypassed.
File: StableModule.sol
```solidity
function executeDeposit(
    address _account,
    uint64 _executableAtTime,
    FlatcoinStructs.AnnouncedStableDeposit calldata _announcedDeposit
) external whenNotPaused onlyAuthorizedModule returns (uint256 _liquidityMinted) {
    uint256 depositAmount = _announcedDeposit.depositAmount;

    uint32 maxAge = _getMaxAge(_executableAtTime);

    _liquidityMinted = (depositAmount * (10 ** decimals())) / stableCollateralPerShare(maxAge);

    if (_liquidityMinted < _announcedDeposit.minAmountOut)
        revert FlatcoinErrors.HighSlippage(_liquidityMinted, _announcedDeposit.minAmountOut);

    _mint(_account, _liquidityMinted);

    vault.updateStableCollateralTotal(int256(depositAmount));

    revert FlatcoinErrors.AmountTooSmall({amount: totalSupply(), minAmount: MIN_LIQUIDITY});
```
First, Bob mints 10000 wei shares via executeDeposit function. Next, Bob withdraws 9999 wei shares via the executeWithdraw. In the end, Bob successfully owned only 1 wei share, which is the prerequisite for this attack.
Part 2 - Donate or transfer assets to the vault to inflate the assets per share
The vault tracks the number of collateral within the state variables. Thus, simply transferring rETH collateral to the vault directly will not work, and the assets per share will remain the same.
To work around this, Bob creates a large number of accounts (with different wallet addresses). He could choose any or both of the following methods to indirectly transfer collateral to the LP pool/vault to inflate the assets per share:
1) Open a large number of leveraged long positions with the intention of incurring large amounts of losses. The long positions' losses are the gains of the LPs, and the collateral per share will increase.
2) Open a large number of leveraged long positions till the max skew of 120%. Thus, this will cause the funding rate to increase, and the long will have to pay the LPs, which will also increase the collateral per share.
Triggering rounding error
The stableCollateralPerShare will be inflated at this point. Following is the formula used to determine the number of shares minted to the depositor.
If the depositAmount by the victim is not sufficiently large enough, the amount of shares minted to the depositor will round down to zero.
```solidity
_collateralPerShare = (stableBalance * (10 ** decimals())) / totalSupply;
_liquidityMinted = (depositAmount * (10 ** decimals())) / _collateralPerShare
```
Finally, the attacker withdraws their share from the pool. Since they are the only ones with any shares, this withdrawal equals the balance of the vault. This means the attacker also withdraws the tokens deposited by the victim earlier.
Malicious users could steal the assets of the victim.

## Recommendation
A MIN_LIQUIDITY amount of shares needs to exist within the vault to guard against a common inflation attack.
However, the current approach of only checking if the totalSupply() < MIN_LIQUIDITY is not sufficient, and could be bypassed by making use of the withdraw function.
A more robust approach to ensuring that there is always a minimum number of shares to guard against inflation attack is to mint a certain amount of shares to zero address (dead address) during contract deployment (similar to what has been

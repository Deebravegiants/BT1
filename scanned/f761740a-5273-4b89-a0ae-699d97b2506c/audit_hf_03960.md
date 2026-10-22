# [H] Curve V2 Vaults can be drained because

## Summary
Severity: High
Contest weight: 0.8940
Dataset id: 20310
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CurveV2CryptoEthOracle.registerPool takes checkReentrancy parameters and this
should be True only for pools that have
0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE tokens and this is validated here.
```solidity
address public constant ETH = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
...
// Only need ability to check for read-only reentrancy for pools containing native Eth.
if (checkReentrancy) {
    if (tokens[0] != ETH && tokens[1] != ETH) revert MustHaveEthForReentrancy();
}
```
This Oracle is meant for Curve V2 pools and the ones I've seen so far use WETH
address instead of 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE (like Curve V1)
and this applies to all pools listed by Tokemak.
For illustration, I'll use the same pool used to test proper registration. The test is for
CRV_ETH_CURVE_V2_POOL but this applies to other V2 pools including rETH/ETH. The
pool address for CRV_ETH_CURVE_V2_POOL is
0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511 while token address is
0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d.
If you interact with the pool, the coins are: 0 - WETH -
0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 1 - CRV -
0xD533a949740bb3306d119CC777fa900bA034cd52
So how can WETH be reentered?! Because Curve can accept ETH for WETH pools.
A look at the pool again shows that Curve uses python kwargs and it includes a
variable use_eth for exchange, add_liquidity, remove_liquidity and
remove_liquidity_one_coin.
When use_eth is true, it would take msg.value instead of transfer WETH from user.
And it would make a raw call instead of transfer WETH to user.
If raw call is sent to user, then they could reenter LMP vault and attack the protocol
and it would be successful cause CurveV2CryptoEthOracle would not check for
reentrancy in getPriceInEth
```solidity
// Checking for read only reentrancy scenario.
if (poolInfo.checkReentrancy == 1) {
    // This will fail in a reentrancy situation.
    cryptoPool.claim_admin_fees();
}
```
A profitable attack that could be used to drain the vault involves
• Deposit shares at fair price
• Remove liquidity on Curve and updateDebtReporting in LMPVault with view
only reentrancy
• Withdraw shares at unfair price
The protocol could be attacked with price manipulation using Curve read only
reentrancy. The consequence would be fatal because getPriceInEth is used for
evaluating debtValue and this evaluation decides shares and debt that would be
burned in a withdrawal. Therefore, an inflated value allows attacker to withdraw too
many asset for their shares. This could be abused to drain assets on LMPVault.
The attack is cheap, easy and could be bundled in as a flashloan attack. And it puts
the whole protocol at risk cause a large portion of their deposit would be on Curve
V2 pools with WETH token.

## Recommendation
If CurveV2CryptoEthOracle is meant for CurveV2 pools with WETH (and no
0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE), then change the ETH
address to weth. As far as I can tell Curve V2 uses WETH address for ETH but this
needs to be verified.
```solidity
if (tokens[0] != WETH && tokens[1] != WETH) revert MustHaveEthForReentrancy();
```

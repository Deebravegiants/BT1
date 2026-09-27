# [C] 5.1.4 Use of spot price inSponsorVaultleads to sandwich attack.

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** SponsorVault.sol#L
**Description:** There is a special role sponsor in the protocol. Sponsors can cover the liquidity fee and transfer fee
for users, making it more favorable for users to migrate to the new chain. Sponsors can either provide liquidity
for each adopted token or provide the native token in theSponsorVault. If the native token is provided, the
SponsorVaultwill swap to the adopted token before transferring it to users.
contract SponsorVault is ISponsorVault, ReentrancyGuard, Ownable {
...
function reimburseLiquidityFees(
address _token,
uint256 _liquidityFee,
address _receiver
) external override onlyConnext returns (uint256) {
...
uint256 amountIn = tokenExchange.getInGivenExpectedOut(_token, _liquidityFee);
amountIn = currentBalance >= amountIn? amountIn : currentBalance;
// sponsored fee may end being less than _liquidityFee due to slippage
sponsoredFee = tokenExchange.swapExactIn{value: amountIn}(_token, msg.sender);
...
}
}

The spot AMM price is used when doing the swap. Attackers can manipulate the value ofgetInGivenExpectedOut
and makeSponsorVaultsell the native token at a bad price. By executing a sandwich attack the exploiters can
drain all native tokens in the sponsor vault.
For the sake of the following example, assume that_tokenisUSDCand native token isETH, the sponsor tries to
sponsor 100usdcto the users:

- Attacker first manipulates the DEX and makes the exchange of 1 ETH = 0.1 USDC.
- getInGivenExpectedOutreturns100 / 0.1 = 1000.
- tokenExchange.swapExactInbuys 100USDCwith 1000ETH, causing theETHprice to decrease even lower.
- Attacker buysETHat a lower prices and realizes a profit.
**Recommendation:** Instead of relying on DEXe’s spot price the sponsor vault should rely instead on price quotes
which are harder to manipulate, like those provided by an oracle (e.g. chainlinkprice,uniswapTWAP). The
SponsorVaultshould fetch the oracle price and compare it against the spot price. TheSponsorVaultshould
either revert or use the oracle price when the spot price deviates from the oracle price.
**Connext:** Solved in PR 1595.
**Spearbit:** Verified.

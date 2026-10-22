# [H] Two Pyth prices can be used in the same trans-

## Summary
Severity: High
Contest weight: 0.7855
Dataset id: 22576
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pyth oracles use a pull model, where the consumer of the price needs to provide a signed price from an offline provider. There are no guarantees that the price at the current time is the freshest price, which means an attacker can enter an LP position at one base price, and exit in another, all in the same transaction. The OracleMaker and SpotHedgeBaseMaker both allow LPs to contribute funds in exchange for getting an LP position. Outside of the requirment that the current price is within the maxAge, there are no other freshness checks. An attacker can create a contract which, given two signed base prices, calls updatePrice() and deposit()s at the lower price, then calls updatePrice() at the higher price, and calls withdraw() at the higher price, for a risk-free profit. For both the OracleMaker and the SpotHedgeBaseMaker, there are no fees for doing deposit()/withdraw(), and a flash loan can be used to magnify the effect of any price difference between two oracle readings. While both makers support a having a whitelist for who is able to deposit/withdraw, the code doesn’t require one, makers anticipate having to deal with malicious LPs. It appears that the whitelist contain sufficient capital. The fact that there is a maxAge available does not prevent the issue, because Pyth updates are multiple times a second, whereas a block can only have one timestamp. Value accrual that should have gone to the existing LPs is siphoned off by the attacker. The number of shares given depends on whatever the most recently stored price is:
```solidity
// File: src/maker/OracleMaker.sol : OracleMaker.deposit()
#1
189 @> uint256 price = _getPrice();
...
201 @> uint256 vaultValueXShareDecimals = _getVaultValueSafe(vault, price).formatDecimals(
INTERNAL_DECIMALS,
shareDecimals
);
uint256 amountXShareDecimals = amountXCD.formatDecimals(collateralToken.decimals(), shareDecimals);
206:@> shares = (amountXShareDecimals * totalSupply()) / vaultValueXShareDecimals;
/src/maker/OracleMaker.sol#L189-L206
```
The amount of collateral given back is based on whatever the most recently stored price is:
```solidity
// File: src/maker/OracleMaker.sol : OracleMaker.withdraw()
#2
uint256 redeemedRatio = shares.divWad(totalSupply());
...
uint256 price = _getPrice();
242 @> uint256 vaultValue = _getVaultValueSafe(vault, price);
IERC20Metadata collateralToken = IERC20Metadata(_getAsset());
244 @> uint256 withdrawnAmountXCD = vaultValue.mulWad(redeemedRatio).formatDecimals(
INTERNAL_DECIMALS,
collateralToken.decimals()
247:
);
/src/maker/OracleMaker.sol#L234-L247
```
The SpotHedgeBaseMaker has the same issue.

## Recommendation
Require that LP deposits and withdrawals be done by the trusted relayers

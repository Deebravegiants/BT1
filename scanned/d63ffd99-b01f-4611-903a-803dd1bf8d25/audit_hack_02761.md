# [M] EulerStrategy's asset value can become understated if Euler deposit fails

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L49-L55
Type: audit-issue

## Details
# EulerStrategy's asset value can become understated if Euler deposit fails

## Summary

Euler depositing has a small chance of silent failure. In this case USDC is kept on the balance of the EulerStrategy and do not taken into account in net asset value calculations _balanceOf() performs. This can be gamed by an informed user, depositing while this holds to obtain more shares while NAV is understated.

## Vulnerability Detail

Currently only assets in Euler are reported in NAV calculation of EulerStrategy. Apart from direct USDC transfer, there is a small chance of Euler do not processing the deposit. Also, it looks to be viable to craft the transaction so that deposit be silently failed. This way there is a small change an attacker can deposit without NAV increment, which provides a way to obtain a heavily inflated number of shares.

For example, there is 10^6 USDC and the same number of shares, attacker deposit 10^6 USDC 5 times, each time obtaining increasing number of shares: first 10^6, then 2*10^6, then 4*10^6, then 8*10^6, then 16*10^6, totalling 31*10^6, i.e. he will own `31/32` of the pool, while providing `5/6` of the assets.

## Impact

In this situation of forcing Euler deposit to silently malfunction an attacker will be able to steal current stakers' funds by inflating the shares.

## Code Snippet

EulerStrategy calls Euler for the depositing of the whole USDC balance:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L49-L55

Euler deposit() reads sender's balance and deposit the corresponding amount:

https://github.com/euler-xyz/euler-contracts/blob/dfe600640e5e7a2eae1c26b768bbc1141bb4c9b9/contracts/modules/EToken.sol#L136-L150

```solidity
    /// @notice Transfer underlying tokens from sender to the Euler pool, and increase account's eTokens
    /// @param subAccountId 0 for primary, 1-255 for a sub-account
    /// @param amount In underlying units (use max uint256 for full underlying token balance)
    function deposit(uint subAccountId, uint amount) external nonReentrant {
        (address underlying, AssetStorage storage assetStorage, address proxyAddr, address msgSender) = CALLER();
        address account = getSubAccount(msgSender, subAccountId);

        updateAverageLiquidity(account);
        emit RequestDeposit(account, amount);

        AssetCache memory assetCache = loadAssetCache(underlying, assetStorage);

        if (amount == type(uint).max) {
            amount = callBalanceOf(assetCache, msgSender);
        }
```

However, the reading of the balance is done with low-level call, which failure do not revert the operation, and zero amount is reported instead:

https://github.com/euler-xyz/euler-contracts/blob/dfe600640e5e7a2eae1c26b768bbc1141bb4c9b9/contracts/BaseLogic.sol#L313-L325

```solidity
    function callBalanceOf(AssetCache memory assetCache, address account) internal view FREEMEM returns (uint) {
        // We set a gas limit so that a malicious token can't eat up all gas and cause a liquidity check to fail.

        (bool success, bytes memory data) = assetCache.underlying.staticcall{gas: 200000}(abi.encodeWithSelector(IERC20.balanceOf.selector, account));

        // If token's balanceOf() call fails for any reason, return 0. This prevents malicious tokens from causing liquidity checks to fail.
        // If the contract doesn't exist (maybe because selfdestructed), then data.length will be 0 and we will return 0.
        // Data length > 32 is allowed because some legitimate tokens append extra data that can be safely ignored.

        if (!success || data.length < 32) return 0;

        return abi.decode(data, (uint256));
    }
```

The rationale of that is clear, but the small drawback effect here is this call can fail silently, for example if the user is supplied precisely that much gas so it will be enough gas for all operations before the `balanceOf` call and not enough gas to fit into 200k limit and gas limits become mandatory (say https://github.com/ethereum/EIPs/issues/1930 be implemented in the future). In this case the call be reverted, but the transaction will proceed with callBalanceOf() returning 0.

After that EulerStrategy's NAV reported will be understated as it doesn't include its USDC balance:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L45-L47

## Tool used

Manual Review

## Recommendation

Consider adding current USDC balance to net asset value calculations:

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L45-L47

```solidity
  function _balanceOf() internal view override returns (uint256) {
-   return EUSDC.balanceOfUnderlying(address(this));
+   return want.balanceOf(address(this)) + EUSDC.balanceOfUnderlying(address(this));
  }
```

Also, want balance utilization can be added to the `_withdraw(uint256 _amount)` logic.

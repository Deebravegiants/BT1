# [H] Adversary can sandwich oracle updates to exploit BLVaultLido

## Summary
Severity: High
Contest weight: 0.6366
Dataset id: 20438
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BLVaultLido added a mechanism to siphon off all wstETH obtained from the vault could be manipulated to the attackers gain. This mitigation however does not fully address the issue and the same issue is still exploitable by sandwiching oracle update.

```solidity
uint256 wstethOhmPrice = manager.getTknOhmPrice();
uint256 expectedWstethAmountOut = (ohmAmountOut * wstethOhmPrice) / _OHM_DECIMALS;

// Take any arbs relative to the oracle price for the Treasury and return the rest to the owner
uint256 wstethToReturn = wstethAmountOut > expectedWstethAmountOut
    ? expectedWstethAmountOut
    : wstethAmountOut;
if (wstethAmountOut > wstethToReturn)
    wsteth.safeTransfer(TRSRY(), wstethAmountOut - wstethToReturn);
```

In the above lines we can see that the current oracle price is used to calculate the expected amount of wstETH to return to the user. In theory this should prevent the attack but an attacker can side step this sandwiching the oracle update. Example: The POC is very similar to before except now it's composed of two transactions sandwiching the oracle update. Chainlink oracles have a tolerance threshold of 0.5% before updating so we will use that as our example value. The current price is assumed to be 0.995 wstETH/OHM. The oracle price (which is about to be updated) is currently 1:1

Transaction 1:
Balances before attack (0.995:1)
Liquidity: 79.8 OHM 80.2 wstETH
Adversary: 20 wstETH
Swap OHM so that pool price matches pre-update oracle price:
Liquidity: 80 OHM 80 wstETH
Adversary: -0.2 OHM 20.2 wstETH
Balances after adversary has deposited to the pool:
Liquidity: 100 OHM 100 wstETH
Adversary: -0.2 OHM 0.2 wstETH
Balances after adversary sells wstETH for OHM (0.5% movement in price):
Liquidity: 99.748 OHM 100.252 wstETH
Adversary: 0.052 OHM -0.052 wstETH
Sandwiched Oracle Update:
Oracle updates price of wstETH to 0.995 OHM. Since the attacker already sold wstETH to balance the pool to the post-update price they will be able to withdraw the full amount of wstETH.

Transaction 2:
Balances after adversary removes their liquidity:
Liquidity: 79.798 OHM 80.202 wstETH
Adversary: 0.052 OHM 19.998 wstETH
Balances after selling profited OHM:
Liquidity: 79.849 OHM 80.152 wstETH
Adversary: 20.05 wstETH
As shown above it's still profitable to exploit the vault by sandwiching the oracle updates. With each oracle update the pool can be repeatedly attacked causing large losses. Vault will be attacked repeatedly for large losses

## Recommendation
To prevent this I would recommend locking the user into the vault for some minimum amount of time (i.e. 24 hours)

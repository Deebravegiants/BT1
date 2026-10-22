# [C] Confused Deputy in contributeToPool()

## Summary
Severity: Critical
Contest weight: 0.8929
Dataset id: 12116
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the GatherCore contract, the isPoolCurrency global variable indicates if the current pool uses an ERC20 or ETH as the currency. When isPoolCurrency, the corresponding ERC20 address is set at poolCurrency. All the following asset movements such as contributePoolCurrency() and sendPoolCurrencyForRefund() rely on the ERC20 contract deployed at poolCurrency. Based on that, there are two ways for contributors to transfer assets into the pool. If the pool uses ERC20, a contributor should invoke contributePoolCurrency(). If the pool uses ETH, contributeToPool() should be called. Here, we identiﬁed a confused deputy issue in both of them. As shown in the code snippet below, both functions collect the assets, implicitly (ETH) or explicitly (ERC20), before calling contribute() to update the internal asset records. However, there's no sanity check to ensure that the current pool is conﬁgured with the asset that the msg.sender is sending in.

```solidity
function contributePoolCurrency(uint256 _amount)
    external
    require(
        poolCurrency.balanceOf(msg.sender) >= _amount,
        "BALANCE < CONTRIBUTION"
    );
    poolCurrency.safeTransferFrom(msg.sender, address(this), _amount);
    contribute(msg.sender, _amount);
```

```solidity
function contributeToPool()
    external
    payable
    contribute(msg.sender, msg.value);
```

For example, a bad actor could send in 0.001 ETH with contributeToPool() to top-up 1015 poolCurrency. If poolCurrency is USDT which has 6 decimals, the bad actor could invoke withdrawContribution() right after the contributeToPool() call and get 1 millions USDT back. On the other hand, if a bad actor is about to exploit this vulnerability through contributePoolCurrency() with a similar trick mentioned above, the poolCurrency.balanceOf() and poolCurrency.safeTransferFrom() calls fail as the compiler is likely to check the code size of the poolCurrency address. Since a pool conﬁgured with ETH as the currency has poolCurrency == address(0), the attack through contributePoolCurrency() could not happen.

## Recommendation
Check isPoolCurrency in contributePoolCurrency() and contributeToPool().

```solidity
function contributeToPool()
    external
    payable
    require(!isPoolCurrency, "POOL_CONTRIBUTION_MISMATCH");
    contribute(msg.sender, msg.value);
```

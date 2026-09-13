# [M] **5.3.2** L1BlastBridge._initiateBridgeERC20() **directly sends** _amount **of ETH without converting to 18 dec-

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
imals**

**Severity:** Medium Risk

**Context:** L1BlastBridge.sol#L221-L233, L2BlastBridge.sol#L

**Description:** L1BlastBridge._initiateBridgeERC20()initiates a L1!L2 deposit transaction as shown:

```
portal.depositTransaction(
Predeploys.L2_BLAST_BRIDGE,
_amount,
RECEIVE_DEFAULT_GAS_LIMIT,
false,
abi.encodeWithSelector(
L2BlastBridge.finalizeBridgeETHDirect.selector,
_from,
_to,
USDConversions._convertDecimals(_amount, ethYieldToken.decimals, USDConversions.WAD_DECIMALS),
_extraData
)
);
```
It calls L2BlastBridge.finalizeBridgeETHDirect() with USDConversions._convertDecimals(_amount,
ethYieldToken.decimals, USDConversions.WAD_DECIMALS), but sends _amount of ETH through
OptimismPortal.

If a futureethYieldTokenhas more/less than 18 decimals, this will sending the wrong amount of ETH and the
following check infinalizeBridgeETHDirect()will fail:

```
require(msg.value == _amount, "StandardBridge: amount sent does not match amount required");
```
**Recommendation:** Consider sending_amountwith 18 decimals of ETH throughOptimismPortalas well:

```
+ uint256 ethAmount = USDConversions._convertDecimals(_amount, ethYieldToken.decimals,
,! USDConversions.WAD_DECIMALS);
portal.depositTransaction(
Predeploys.L2_BLAST_BRIDGE,
```
- _amount,
+ ethAmount,
    RECEIVE_DEFAULT_GAS_LIMIT,
    false,
    abi.encodeWithSelector(
       L2BlastBridge.finalizeBridgeETHDirect.selector,
       _from,
       _to,
- USDConversions._convertDecimals(_amount, ethYieldToken.decimals, USDConversions.WAD_DECIMALS),
+ ethAmount,
    _extraData
    )
);


```
DRAFT
```

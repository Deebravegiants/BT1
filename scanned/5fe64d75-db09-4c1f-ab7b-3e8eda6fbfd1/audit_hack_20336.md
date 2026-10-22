# [M] 5.2.2 A malicioussettingscontract can callonOwnershipTransferred()to take over pair

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** StandardSettings.sol#L118-L

**Description:** The functiononOwnershipTransferred()can be called from a pair viacall(). This can be done
either beforetransferOwnership()or after it. If it is called before then it updates theAssetRecipient. It can
only be called after thetransferOwnership()when an alternative (malicious) settings contract is used. In that
situationpairInfos[]is overwritten and the original owner is lost; so effectively the pair can be taken over.

Note: if the settings contract is malicious then there are different ways to take over the pair, but using this approach
the vulnerabilities can be hidden.


```
function onOwnershipTransferred(address prevOwner, bytes memory) public payable {
ILSSVMPair pair = ILSSVMPair(msg.sender);
require(pair.poolType() == ILSSVMPair.PoolType.TRADE, "Only TRADE pairs");
```
```
}
```
**Recommendation:**

1. InonOwnershipTransferred()check thataddress(this)is the owner of the pair.
2. InonOwnershipTransferred()check thatpairInfos[]hasn't been used before.
3. As an extra protection, in functioncall()ofLSSVMPair, disallow callingonOwnershipTransferred()

Note: also see related issue "Functioncall()is risky and can be restricted further".

**Sudorandom Labs:** Solved in PR#34.

**Spearbit:** Verified that PR#34 implements Recommendation (3).

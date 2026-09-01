# [M] Penrose#`unregisterContract()` cannot unregister `OriginsMarket`.

## Summary
Severity: Medium
Chain: Smart contract
Component: Tapioca--Lending-Engine-
Published: 2024-06-10
Source: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/29
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x96710a7fc6a2617a260d9aad9e47b9609649937f822155d7674dc669b939732d
**Severity:** medium

**Description:**
### Description

1. When `Origins` is registered, Penrose#`addOriginsMarket()` does not update`clonesOf` and `masterContractOf` state variable unlike Penrose#`addBigBang()`.

```soldity
function addBigBang(address mc, address _contract) 
	external onlyOwner registeredBigBangMasterContract(mc) {
	
	if (isMarketRegistered[_contract]) revert AlreadyAdded();
	//<-------------- @audit
	isMarketRegistered[_contract] = true;
	clonesOf[mc].push(_contract);
	//<-------------------------------
	masterContractOf[_contract] = mc;
	allBigBangMarkets.push(_contract);
	emit RegisterBigBang(_contract, mc);
}
	
function addOriginsMarket(address _contract) external onlyOwner {	
	if (isOriginRegistered[_contract]) revert AlreadyAdded();	
	//<-------------- @audit -- It has not same logic like `addBigBang`
	isOriginRegistered[_contract] = true;
	allOriginsMarkets.push(_contract);
	emit RegisterOrigins(_contract);
}
```

2. But when `Origins` is unregistered, Penrose#`unregisterContract()` is trying to delete `clonesOf` and does not update `isOriginRegistered` flag.

```soldity
function unregisterContract(address mkt, uint256 marketType) external onlyOwner {

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Tapioca--Lending-Engine--0x5bee198f5b060eecd86b299fdbea6b0c07c728dd/issues/29_

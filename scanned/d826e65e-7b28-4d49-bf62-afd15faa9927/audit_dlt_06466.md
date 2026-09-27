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

	address _mc = masterContractOf[mkt];
	// set `isMarketRegistered` to false and remove `masterContractOf`
	
	//<----------------------------- @audit 
	isMarketRegistered[mkt] = false;
	delete masterContractOf[mkt];
	//<-------------------------------------------
	
	// remove it from `allBigBangMarkets` or `allOriginsMarkets`	
	uint256 index;
	if (marketType == 1) {
		index = _findBigBangIndex(allBigBangMarkets, mkt);
		allBigBangMarkets[index] = allBigBangMarkets[allBigBangMarkets.length - 1];
		allBigBangMarkets.pop();
	} else if (marketType == 2) {
		index = _findBigBangIndex(allOriginsMarkets, mkt);
		allOriginsMarkets[index] = allOriginsMarkets[allOriginsMarkets.length - 1];
		allOriginsMarkets.pop();
	}
	
	// remove it from clonesOf
	//<----------------------------- @audit 
	index = _findBigBangIndex(clonesOf[_mc], mkt);	
	clonesOf[_mc][index] = clonesOf[_mc][clonesOf[_mc].length - 1];
	clonesOf[_mc].pop();
	//<-------------------------------------------
	
	emit UnregisterContract(mkt);
}
```
### Attack Scenario:

1. Penrose calls `unregisterContract()` to unregister `Origins`.
2. It will be always reverted.

### Attachments
#### 1. Proof of Concept (PoC) File:

- Please append PenroseTest#`test_penrose_unregister_origins()` as follows.

```solidity
...
import {Origins} from "contracts/markets/origins/Origins.sol";
import {ITapiocaOracle} from "tapioca-periph/interfaces/periph/ITapiocaOracle.sol";

contract PenroseTest is UsdoTestHelper {
	...
	function test_penrose_unregister_origins() public {
		
		Origins origins;
		
		origins = createOrigins(
			address(this),
			address(yieldBox),
			address(asset),
			assetYieldBoxId,
			address(collateral),
			collateralYieldBoxId,
			ITapiocaOracle(address(oracle)),
			0,			
			99999
		);
		
		penrose.addOriginsMarket(address(origins));
		
		vm.expectRevert(Penrose.AddressNotValid.selector);
        penrose.unregisterContract(address(origins), 2);
	}
}
```

- Place this PoC into `test/Penrose.t.sol`  and execute with
```
forge test --match-test test_penrose_unregister_origins
```

#### 2. Revised Code File (Optional)

Please update Penrose#`unregisterContract()` as follows.

```diff
function unregisterContract(address mkt, uint256 marketType) external onlyOwner {

++	if (marketType == 1) {
	address _mc = masterContractOf[mkt];
	// set `isMarketRegistered` to false and remove `masterContractOf`
	isMarketRegistered[mkt] = false;
	delete masterContractOf[mkt];
++	} else if (marketType == 2) {
++		isOriginRegistered[mkt] = false;
++	}	
	
	
	// remove it from `allBigBangMarkets` or `allOriginsMarkets`	
	uint256 index;
	if (marketType == 1) {
		index = _findBigBangIndex(allBigBangMarkets, mkt);
		allBigBangMarkets[index] = allBigBangMarkets[allBigBangMarkets.length - 1];
		allBigBangMarkets.pop();
	} else if (marketType == 2) {
		index = _findBigBangIndex(allOriginsMarkets, mkt);
		allOriginsMarkets[index] = allOriginsMarkets[allOriginsMarkets.length - 1];
		allOriginsMarkets.pop();
	}
	
++	if (marketType == 1) {
	// remove it from clonesOf
	index = _findBigBangIndex(clonesOf[_mc], mkt);	
	clonesOf[_mc][index] = clonesOf[_mc][clonesOf[_mc].length - 1];
	clonesOf[_mc].pop();
++	}
	
	emit UnregisterContract(mkt);
}
```

**Description**\
Describe the context and the effect of the vulnerability.

**Attack Scenario**\
Describe how the vulnerability can be exploited.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
  
**Files:**
  - Tapicao_unix515.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmQ7Ra39h8r1q9GGjYQAsv9p1A49ZQxPkGTc9cqDtfKrHa)

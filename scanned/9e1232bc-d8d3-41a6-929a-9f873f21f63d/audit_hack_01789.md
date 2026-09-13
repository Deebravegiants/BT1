# [M] Presence of testnet code

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
Based on the discussions with pStake team and in-line comments, there are a few instances of code and commented code in the code base under audit that are not finalized for mainnet deployment.

#### Examples


**code/contracts/PSTAKE.sol:L25-L37**
```solidity
function initialize(address pauserAddress) public virtual initializer {
	__ERC20_init("pSTAKE Token", "PSTAKE");
	__AccessControl_init();
	__Pausable_init();
	_setupRole(DEFAULT_ADMIN_ROLE, _msgSender());
	_setupRole(PAUSER_ROLE, pauserAddress);
	// PSTAKE IS A SIMPLE ERC20 TOKEN HENCE 18 DECIMAL PLACES
	_setupDecimals(18);
	// pre-allocate some tokens to an admin address which will air drop PSTAKE tokens
	// to each of holder contracts. This is only for testnet purpose. in Mainnet, we
	// will use a vesting contract to allocate tokens to admin in a certain schedule
	_mint(_msgSender(), 5000000000000000000000000);
}
```

The initialize function currently mints all the tokens to msg.sender, however the goal for mainnet is to use a vesting contract which is not present in the current code.

#### Recommendation

It is recommended to fully test the **final** code before deployment to the mainnet.

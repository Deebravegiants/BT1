# [M] 5.2.8 Hardcode or whitelist the Thorswapvaultaddress

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** ThorSwapFacet.sol#LL104C27-L104C
**Description:** The issue with this code is that thedepositWithExpiryfunction allows the user to enter any arbitrary
vault address, which could potentially lead to a loss of tokens. If a user enters an incorrect or non-existentvault
address, the tokens could be lost forever. There should be some validation on thevaultaddress to ensure that it
is a valid and trusted address before allowing deposits to be made to it.

- Router


```
// Deposit an asset with a memo. ETH is forwarded, ERC-20 stays in ROUTER
function deposit(address payable vault, address asset, uint amount, string memory memo) public
,! payable nonReentrant{
uint safeAmount;
if(asset == address(0)){
safeAmount = msg.value;
bool success = vault.send(safeAmount);
require(success);
} else {
require(msg.value == 0, "THORChain_Router: unexpected eth"); // protect user from
,! accidentally locking up eth
if(asset == RUNE) {
safeAmount = amount;
iRUNE(RUNE).transferTo(address(this), amount);
iERC20(RUNE).burn(amount);
} else {
safeAmount = safeTransferFrom(asset, amount);// Transfer asset
_vaultAllowance[vault][asset] += safeAmount;// Credit to chosen vault
}
}
emit Deposit(vault, asset, safeAmount, memo);
}
```
**Recommendation:** Hardcode or whitelist thevaultaddress.
Asgard Vault Addresses can be seen from here.
**LiFi:** LiFi Team claims that they are validating the address on the backend side.
**Spearbit:** Acknowledged.

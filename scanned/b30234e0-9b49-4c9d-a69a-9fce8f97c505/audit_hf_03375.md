# [M] Can’t pause or remove a minter

## Summary
Severity: Medium
Contest weight: 0.4437
Dataset id: 18405
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The project is supposed to be self-governing. Token owners are able to suggest new minters and collateral. The auction mechanism allows participants to remove collateral from the system if it’s deemed unhealthy. But, there’s no way to remove a registered minter.

Why would you want to remove a registered minter? Because they can have bugs that could break the whole system. The current minter, MintingHub, for example, implements a novel auction mechanism to price collateral instead of choosing the industry standard Chainlink oracles. While I support the idea of having a fully decentralized system, it does add additional risk to the project. A risk that’s taken not only by the protocol team but every ZCHF holder as well.

Obviously, these are just hypotheticals. But, the system is not equipped to handle a scenario where the minter malfunctions.

## Proof of Concept
After a minter is suggested you have generally 10 days to deny it. After that, there’s no way to remove it:
    
```solidity
function denyMinter(address _minter, address[] calldata _helpers, string calldata _message) override external {
    if (block.timestamp > minters[_minter]) revert TooLate();
    reserve.checkQualified(msg.sender, _helpers);
    delete minters[_minter];
    emit MinterDenied(_minter, _message);
}
```

## Recommendation
Implement the ability for token holders to temporarily pause a minter as well as remove it altogether.

I have thought about the ability to remove old minters, but decided against it.

Instead, experimental minters should come with their own limits (time, pause function, volume limits, etc.). They are free to include that. Minters that do not include it, can be expected to be denied unless they have been really thoroughly audited.

So in fact, it is possible to pause a minter assuming the minter supports that functionality.

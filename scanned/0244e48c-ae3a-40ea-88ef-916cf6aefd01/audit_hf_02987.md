# [C] An attacker can add new ZKT tokens and steal all of the fees from them

## Summary
Severity: Critical
Contest weight: 0.0954
Dataset id: 16648
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside the Tsunami contract we have a function to add new ZKT ERC20 tokens which has the onlyAdmin modifier that makes sure only the admin of the protocol can call it.
token_contract_address) public onlyAdmin {
bytes32 zktHash = keccak256(abi.encode(symbol));
uint256 zktId = uint256(zktHash);
bool zktExists = zkts.contains(zktId);
if (zktExists) {
revert("ZKT already exists for this token.");
token_contract_address);
zkts.set(uint256(bytes32(bytes(symbol))), erc20);
ZKTBase(erc20).setUnit(10000000000000000);
ZKTBase(erc20).setAgency(payable(msg.sender));
ZKTBase(erc20).setAdmin(msg.sender);
It checks if the token is already added and then calls newZKTERC20 from the ZKTERC20Factory contract.
The problem comes from the fact that newZKTERC20 is a public function without access control and anyone can call it:
ZKT_Tsunami.md
ZKTERC20 zktERC20 = new ZKTERC20(_token, transfer, burn);
zktERC20.setAdmin(admin);
access to critical functions for the protocol.
Let's take a look at the following scenario:
). An attacker calls newZKTERC20 and adds a new token.
him.
Another problem newZKTERC20 is missing any checks and an attacker can add already existing tokens and

## Recommendation
Add an access control modifier that makes sure only the deployer can call newZKTERC20. Also, consider changing the visibility to internal, so that the function cannot be called on its own and all of the checks are required.

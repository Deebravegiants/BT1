# [H] TradableSettings: tokens can only be added in one chain

## Summary
Severity: High
Contest weight: 0.6025
Dataset id: 16161
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Tokens can only be added onto a single sideVault in a different chain using the TradableSettings contract. This is due to the fact that calling function addAcceptedToken() will add the token on both the sideVault and TradableSettings contract, preventing future calls to the same function on the TradableSettings contract, since there is a requirement (require(!tokenExists(_token)) stopping multiple calls with the same token address.
For clarification, take a look at the TradableSettings implementation:
```solidity
function addAcceptedToken(address _token, uint8 _decimals, bool _isActive, address vault) (...) external
{
    require(messageAdapter != address(0x0), "!invalid-message-adapter");
    require(vaultExists(vault), "!invalid-vault-information");
    require(!tokenExists(_token), "!token-already-exists");
    sendMessage(vault, abi.encode("aat", _token, _decimals, _isActive));
    acceptedTokenMap[_token] = AcceptedToken(_token, _decimals, false);
    acceptedTokenList.push(_token);
}
function tokenExists(address token) view public returns(bool) {
    for(uint i = 0; i < acceptedTokenList.length; i++){
        if(acceptedTokenList[i] == token){
            return true;
        }
    }
    return false;
}
```
Note: This is only an issue if the token has the same address in more than one chain.
Note 2: This issue is also found in the deleteAcceptedToken() function.

## Recommendation
Remove the requirement: require(!tokenExists(_token), "!token-already-exists");. Also considering adding tests where multiple sideVaults on multiple side chains are used.

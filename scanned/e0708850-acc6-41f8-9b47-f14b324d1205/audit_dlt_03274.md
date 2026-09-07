# [M] Governance can arbitrarily burn VeToken from any address

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-vetoken
Published: 2022-06-02
Source: https://github.com/code-423n4/2022-05-vetoken-findings/issues/233
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-vetoken/blob/2d7cd1f6780a9bcc8387dea8fecfbd758462c152/contracts/token/VeToken.sol#L30-L34


# Vulnerability details

## Impact
Governance can burn any amount of `VeToken` from any address. 

Unlike `VE3Token` which is minted when users deposit veAsset and burned when users withdraw, the `burn` function in the governance token `VeToken.sol` is unnecessary and open up the risk of malicious/compromised governance burning user's token.

## Recommended Mitigation Steps
Consider removing the function, or modify the burn function so it only allows `msg.sender` to burn the token:
```
function burn(uint256 _amount) external {
    _burn(msg.sender, _amount);
}
```

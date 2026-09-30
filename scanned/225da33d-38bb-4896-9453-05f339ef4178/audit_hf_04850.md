# [M] LenderCommitmentGroup_Smart.sol cannot de-

## Summary
Severity: Medium
Contest weight: 0.5960
Dataset id: 22745
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In LenderCommitmentGroup_Smart.sol, when initializing, it needs to fetch the symbol() for the principalToken and collateralToken. However, it assumes the symbol() returns a string, which is actually OPTIONAL for ERC20 standards. This means it would fail to create pools for these ERC20s. First, let's quote the EIP20 to show symbol() is optional: symbol Returns the symbol of the token. E.g. “HIX”. OPTIONAL - This method can be used to improve usability, but interfaces and other contracts MUST NOT expect these values to be present. function symbol() public view returns (string) The most famous token that uses bytes32 instead of string as symbol() return value is MKR. The contest README states that any tokens compatible with Uniswap V3 should be supported, which includes MKR: https://info.uniswap.org/#/tokens/0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2 We are allowing any standard token that would be compatible with Uniswap V3 to work with our codebase, just as was the case for the with Uniswap V3. At last, let's see the code. _generateTokenNameAndSymbol assumes that both principalToken and collateralToken has a symbol() function that returns string, which is inaccurate. This would revert if we try to create a pool with MKR.
```solidity
function _generateTokenNameAndSymbol(address principalToken, address
    collateralToken)
    internal view
    returns (string memory name, string memory symbol) {
    // Read the symbol of the principal token
    string memory principalSymbol = ERC20(principalToken).symbol();
    // Read the symbol of the collateral token
    string memory collateralSymbol = ERC20(collateralToken).symbol();
    // Combine the symbols to create the name
    name = string(abi.encodePacked("GroupShares-", principalSymbol, "-",
        collateralSymbol));
    // Combine the symbols to create the symbol
    symbol = string(abi.encodePacked("SHR-", principalSymbol, "-",
        collateralSymbol));
}
```
LenderCommitmentGroup_Smart pools cannot be created for ERC20s that does not implement function symbol() public view returns (string).

## Recommendation
Consider using a try-catch, an example would be:
```solidity
function computeSymbol(
    address token
) external view returns (string memory) {
    try IERC20Metadata(token).symbol() returns (string memory tokenSymbol) {
        return tokenSymbol;
    } catch {
        return "???";
    }
}
```

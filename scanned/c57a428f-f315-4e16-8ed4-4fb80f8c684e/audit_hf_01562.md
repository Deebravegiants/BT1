# [M] Tokens that require non-zero allowance cannot be disabled

## Summary
Severity: Medium
Contest weight: 0.6777
Dataset id: 8348
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the g8keepFactory contract, the setPairedTokenSettings function allows the owner to enable or disable a token as a valid paired token. At the end of the function, the Uniswap router is approved to spend an unlimited amount of the token.
```solidity
function setPairedTokenSettings(
    address pairedToken,
    bool allowed,
    uint256 minimumLiquidity
) external onlyOwner {
    if (lockedTokens[pairedToken]) revert TokenLocked();
    allowedPairs[pairedToken] = allowed;
    pairedTokenMinimumLiquidity[pairedToken] = minimumLiquidity;
    IERC20(pairedToken).approve(UNISWAP_V2_ROUTER, type(uint256).max);
```
Some tokens, such as USDT on mainnet, will revert when both the current and new allowance are non-zero, causing the transaction to revert, making it impossible to disable the token as a paired token.
```solidity
function approve(address _spender, uint _value) public onlyPayloadSize(2 * 32) {
    // To change the approve amount you first have to reduce the addresses`
    // allowance to zero by calling `approve(_spender, 0)` if it is not
    // already 0 to mitigate the race condition described here:
    // https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    require(!((_value != 0) && (allowed[msg.sender][_spender] != 0)));
    allowed[msg.sender][_spender] = _value;
    Approval(msg.sender, _spender, _value);
```

## Recommendation
```solidity
function setPairedTokenSettings(
    address pairedToken,
    bool allowed,
    uint256 minimumLiquidity
) external onlyOwner {
    if (lockedTokens[pairedToken]) revert TokenLocked();
    allowedPairs[pairedToken] = allowed;
    pairedTokenMinimumLiquidity[pairedToken] = minimumLiquidity;
    if (allowed) {
        IERC20(pairedToken).approve(UNISWAP_V2_ROUTER, type(uint256).max);
    } else {
        IERC20(pairedToken).approve(UNISWAP_V2_ROUTER, 0);
    }
```

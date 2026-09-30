# [H] Depositing to Pocket is vulnerable to inflation attacks

## Summary
Severity: High
Contest weight: 0.7653
Dataset id: 5073
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When depositing to Pocket, a malicious user can manipulate pricePerShare by donating, so that other users will lose due to rounding down when depositing. Consider the following scenario:
1. Alice deposits 1e18 wei collateral to Pocket.
2. Bob observes Alice's transaction, and frontruns Alice with the following action.
3. Bob deposits 1 wei collateral and mint 1 wei share.
4. Bob transfers 1e18 wei collateral to Pocket, now total assets are 1e18 + 1 wei, and total shares are 1 wei.
5. Alice's transaction is executed, shares = 1 * 1e18 / (1e18 + 1), rounding down to 0, Alice receives 0 share.
6. Bob withdraws 1 wei share and receives 2e18+1 wei collateral.

## Recommendation
According to OZ's explanation of ERC-4626 inflation attacks, there are several recommendations to mitigate inflation attack, such as:
1. The use of an ERC4626 Router does not resolve the issue on its own, as it relies on users to perform slippage control during mint/deposit to prevent losses.
```solidity
function deposit(
    IERC4626 vault,
    address to,
    uint256 amount,
    uint256 minSharesOut
) public payable virtual override returns (uint256 sharesOut) {
    if ((sharesOut = vault.deposit(amount, to)) < minSharesOut) { // @audit: slippage control here
        revert MinSharesError();
    }
}
```
2. Tracking assets internally instead of relying on current token balances. In other words, this requires the protocol to not use balanceOf() to track assets, which does not apply to rebase tokens, such as aToken.
3. Dead Shares (like Uniswap V2).
```solidity
function mint(address to) external lock returns (uint liquidity) {
    // ...
    uint _totalSupply = totalSupply; // gas savings, must be defined here since totalSupply can update in _mintFee
    if (_totalSupply == 0) {
        liquidity = Math.sqrt(amount0.mul(amount1)).sub(MINIMUM_LIQUIDITY);
        _mint(address(0), MINIMUM_LIQUIDITY); // permanently lock the first MINIMUM_LIQUIDITY tokens
    }
```
After we mint the initial 1000 shares to address(0), when the attacker makes a donation, the donated assets will increase the value of these 1000 dead shares, causing the attacker to lose. Consider that the attacker mints 1001 shares, 1000 shares are minted to address(0), and 1 share is minted to the attacker. After that, the attacker donates 1e18 collateral. The attacker immediately loses 1000/1001 * 1e18 collateral.
4. Virtual Shares and Decimals Offset.
This is the method used by OZ ERC4626 and is proven mathematically within OpenZeppelin's documentation. However, this method may significantly increase totalShares, so the assert() statement in BasePocket.registerDeposit() may need to be changed if it is used.
```solidity
assert($.sharesOf[user] < 1e38);
```

# [C] Minter Decimal Precision and Depeg Mismatch

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23400
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Minter doesn't account for depegs, exchange rates and decimal precision mismatch between baseAsset and hilBTCToken, which can result in total loss scenarios for both users and protocol  

Description: Minter supports conversion between two key assets, baseAsset and hilBTCToken:  

```solidity
/// @notice The token address of the base asset accepted for deposit (e.g., WBTC or a stablecoin)
IERC20 public immutable baseAsset;
/// @notice The token address of the HilBTC ERC-20 contract (which the Minter will mint/burn)
IMintableERC20 public immutable hilBTCToken;
```

- baseAsset explicitly can be wBTC, USDC or USDT; these can have various precision such as 8, 6 or 18 depending on the chain  
- hilBTCToken is explicitly always the protocol's synthetic bitcoin token hBTC having 8 decimal precision  

Minter::mint allows users to supply input amount tokens in baseAsset and receive output amount tokens in hilBTCToken with no adjustment for different decimal precision, exchanges rates or depeg events:

```solidity
function mint(
    address to,
    uint256 amount
) external onlyWhitelisted(msg.sender) onlyWhitelisted(to) nonReentrant {
    baseAsset.safeTransferFrom(msg.sender, address(this), amount);
    hilBTCToken.mint(to, amount);
    totalDeposits += amount;
    emit Minted(to, amount);
}
```

Impact: There are multiple negative scenarios that can arise, but the most significant examples are:  

1) baseAsset represents a wrapped form of bitcoin which uses 8 decimal places (eg wBTC) but has currently depegged and is not worth anywhere near the actual bitcoin price:  
- user buys wBTC very cheap from a decentralized exchange due to the depeg  
- user calls Minter::mint passing amount = 1e8 (normally worth 1 BTC but now worth far less due to the depeg)  
- user receives 1e8 worth of hBTC where 1 BTC is 1e8  
- user can then drain x/hBTC liquidity pools since they were credited 1 BTC worth of hBTC even though they didn't provide 1 BTC worth of wBTC since wBTC has depegged  
- in the kick‑off call notes it states that hBTC can always be redeemed for BTC at a 1:1 ratio, so this may also be another way to drain reserves though this likely involves off‑chain components  
- user could also stake the hBTC to earn more yield than they should though this is less immediately impactful  

2) baseAsset represents a stablecoin such as USDC:  
- user deposits 1e6 ($1)  
- user receives 1e6 worth of hBTC which is currently worth around $1,180  
- user can then drain x/hBTC liquidity pools and other similar scenarios as 1) above

## Recommendation
Recommended Mitigation: Minter in its current form can only be safely used with wrapped BTC representations that use 8 decimal places - the first option is to enforce this is the case in the constructor and remove the comment stating that baseAsset can be multiple different assets.  

However as noted baseAsset is intended to be many other different assets eg:  

```solidity
/// @notice The token address of the base asset accepted for deposit (e.g., WBTC or a stablecoin)
IERC20 public immutable baseAsset;
```  

To support different baseAsset as the code currently intends, the mint and redeem functions will need to account for:  
- differences in decimal precision between baseAsset and hilBTCToken  
- exchange rates between baseAsset and hilBTCToken  
- alternatively rename hilBTCToken to hilSyntheticToken and ensure that the synthetic token is always the equivalent of baseAsset  

The code also needs to handle depeg events where the baseAsset even if wBTC can depeg and be worth far less than actual bitcoin, but hBTC is always redeemable 1:1 for native BTC. So if a depeg has occurred minting or redeem should revert. The ideal way to implement this check is via Chainlink price feeds, reverting if a depeg has occurred.  

If Chainlink is not available on specific chains a secondary option could be Uniswap V3 TWAP. A third option could be making the Minter contract pausable and having an off‑chain bot monitor baseAsset for depegs then pause the contract should a depeg occur - but this introduces additional risk related to the offchain bot not functioning correctly.

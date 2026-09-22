# [M] Price Calculation Discrepancy in Asset Conversion

## Summary
Severity: Medium
Chain: Smart contract
Component: Euro-Dollar
Published: 2024-11-04
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/34
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** ACai_sec
**Submission hash (on-chain):** 0x33d536198fecda7c86619265c0e63f9b8400261c847e74836e4591b11fa232c7
**Severity:** medium

**Description:**
**Description**\
A vulnerability exists in the price calculation mechanism between deposits and withdrawals in the InvestToken contract. The issue arises due to inconsistent price references when converting between assets (USDE) and shares, potentially causing users to suffer losses during emergency withdrawals.

**Attack Scenario**\
```solidity
// In InvestToken.sol
function deposit(uint256 assets, address receiver) public returns (uint256 shares) {
    shares = convertToShares(assets);  // Uses currentPrice
    usde.burn(msg.sender, assets);
    _mint(receiver, shares);
}

function withdraw(uint256 assets, address receiver, address owner) public returns (uint256 shares) {
    shares = convertToShares(assets);  // Uses currentPrice for calculation
    _burn(owner, shares);
    usde.mint(receiver, assets);
}

// In YieldOracle.sol
function assetsToShares(uint256 assets) external view returns (uint256) {
    return Math.mulDiv(assets, 10 ** 18, currentPrice);
}

function sharesToAssets(uint256 shares) external view returns (uint256) {
    return Math.mulDiv(shares, previousPrice, 10 ** 18);  // Uses previousPrice
}
```
Consider the following scenario:

Initial state:
```solidity

currentPrice = 100 USDE/share
previousPrice = 90 USDE/share
User deposits 1000 USDE:
```
```solidity
shares = 1000 * (10**18) / 100 = 10 shares  // Using currentPrice
Oracle malfunctions or updates are delayed
User attempts emergency withdrawal:
```

```solidity
assets = 10 * 90 / (10**18) = 900 USDE  // Using previousPrice
Result: User loses 100 USDE (10% loss) due to price calculation discrepancy
```

**Attachments**

1. **Proof of Concept (PoC) File**
```solidity
contract PriceDiscrepancyTest {
    function testPriceDiscrepancy() public {
        // Setup
        address user = address(this);
        uint256 depositAmount = 1000e18;
        
        // Step 1: Deposit
        usde.approve(address(investToken), depositAmount);
        uint256 shares = investToken.deposit(depositAmount, user);
        
        // Step 2: Simulate oracle malfunction
        // (price update delay or oracle address misconfiguration)
        
        // Step 3: Emergency withdrawal
        uint256 withdrawnAmount = investToken.redeem(shares, user, user);
        
        // Assert: withdrawnAmount < depositAmount
        assert(withdrawnAmount < depositAmount);
    }
}
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

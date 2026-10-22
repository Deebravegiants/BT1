# [M] Lender ERC4626 broken compliance for the

## Summary
Severity: Medium
Contest weight: 0.7549
Dataset id: 23026
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
README states the following about ERC4626 compliance:
Q: Is the codebase expected to comply with any EIPs? Can there be/are
there any deviations from the specification? The Lender complies with
here: https://coda.io/d/_dJtHvRlIBOx/Standard-Compliance_su6Wx
The link referenced provides the following compliance specification for mint
function:
Mints exactly shares Vault shares to receiver by depositing assets of
underlying tokens.
Notice that mint must send exactly the amount of shares specified, however
Lender implementation of mint converts shares amount into assets (rounding up),
then back into shares (rounding down). In some circumstances these 2 conversions
might lead to a different amount from the one specified by user. For example:
inventory = 999_999, totalSupply = 1_000_000, mint(999_999 shares) does the
following:
1. Converts shares into assets:
```solidity
amount = previewMint(shares);
...
function previewMint(uint256 shares) public view returns (uint256) {
    (, uint256 inventory, uint256 newTotalSupply) =
        _previewInterest(_getCache());
    return _convertToAssets(shares, inventory, newTotalSupply, /* roundUp:
       */ true);
}
...
function _convertToAssets(
    uint256 shares,
    uint256 inventory,
    uint256 totalSupply_,
    bool roundUp
) internal pure returns (uint256) {
    if (totalSupply_ == 0) return shares;
    return roundUp ? shares.mulDivUp(inventory, totalSupply_) :
        shares.mulDivDown(inventory, totalSupply_);
}
```
assets = roundup(999999 * 999999 / 1000000) = roundup(999998.000001) = 999999
2. Convert assets back into shares:
```solidity
shares = _convertToShares(amount, inventory, cache.totalSupply, /* roundUp:
   */ false);
...
function _convertToShares(
    uint256 assets,
    uint256 inventory,
    uint256 totalSupply_,
    bool roundUp
) internal pure returns (uint256) {
    if (totalSupply_ == 0) return assets;
    return roundUp ? assets.mulDivUp(totalSupply_, inventory) :
        assets.mulDivDown(totalSupply_, inventory);
}
```
shares = rounddown(999999 * 1000000 / 999999) = rounddown(1000000) = 1000000
3. This amount (1000000) is then minted to user (although user has requested to
mint 999999 shares).
This breaks the ERC4626 compliance for the mint function.
which is a tricky situation but still possible, exact steps how it can happen are given
below in Attack Path and POC.
mint function simply converts shares amount to assets amount and uses deposit
with this amount, which converts assets back into shares. This double-conversion
pdate/blob/main/aloe-ii/core/src/Lender.sol#L167-L170
The math for the cases in this issue makes it impossible to find an integer assets
amount which will convert back to original shares amount, like:
• 98 assets -> 98 shares
• 99 assets -> 100 shares
So for 99 shares there is no integer amount of assets that can converts to 99
shares, which is the root cause why simple double-conversion is not enough to
mint exact shares amount via deposit.
Internal pre-conditions
Certain combination of total lender assets, totalSupply and user requested mint
amount. The higher the supply/assets ratio, the higher the probability of incorrect
withdrawal amount. This can never happen if assets >= supply. Even though the
protocol is designed such that assets >= supply, it's still possible to have assets <
supply in some tricky edge cases.
External pre-conditions
None
Attack Path
Since protocol is designed for assets >= supply, the first part of the attack is to
show scenario when assets can actually be below supply. One possible way to
achieve this is to exploit borrow rounding error:
• Lender.borrow calculates the borrow units rounding them down:
units = (amount * BORROWS_SCALER) / cache.borrowIndex;
• However, when the borrow inventory is calculated in _previewInterest, the
units => asset amount conversion rounds down too:
uint256 oldBorrows = (cache.borrowBase * cache.borrowIndex) / BORROWS_SCALER;
This means that if we borrow exactly 1 wei (when borrowIndex is greater than ONE,
if it's exactly ONE, then division by borrowIndex is always exact due to
BORROW_SCALER being ONE « 72), then the oldBorrows (borrow inventory) will be
0 (because our integer borrowing units amount is slightly less than exact amount of
units needed for 1 wei of assets due to rounding it down).
This borrow feature allows to reduce assets while keeping totalSupply the same. So
the exact steps to make assets < totalSupply:
1. Make sure that borrowIndex is greater than ONE (deposit, borrow, wait, repay,
redeem to make it so)
2. Deposit some assets (since this is a deposit into an empty Lender, totalAssets
= totalSupply)
3. borrow exactly 1 wei of assets from the Lender (totalAssets decrease by 1)
4. mint the amount of shares equal to current totalSupply - 1 => the actual
minted amount will be equal to totalSupply instead.
the other ways to have assets < totalSupply.
Lender is not ERC4626-compliant. Since this compliance is specifically stated in
contest README, this should make this issue a valid medium.

## Proof of Concept
Add this to Lender.t.sol:
```solidity
function test_mintWrongShares() public {
    // Give this test contract some shares
    deal(address(asset), address(lender), 1e18);
    lender.deposit(1, address(this));
    // Borrow some tokens (so that interest will actually accrue)
    hoax(address(lender.FACTORY()));
    lender.whitelist(address(this));
    lender.borrow(1, address(this));
    // Mock interest model
    uint256 yieldPerSecond = MAX_RATE - 1;
    vm.mockCall(
        address(lender.rateModel()),
        abi.encodeWithSelector(RateModel.getYieldPerSecond.selector, 0.5e18,
            address(lender)),
        abi.encode(yieldPerSecond)
    );
    // Now skip forward in time, but don't modify `lender` state yet
    skip(1);
    lender.repay(2, address(this)); // 2, because the debt has grown a little
    lender.redeem(1, address(this), address(this));
    // deposit again
    lender.deposit(1e6, address(this));
    console.log("Before borrow: totalAssets = %d totalSupply = %d",
        lender.totalAssets(), lender.totalSupply());
    lender.borrow(1, address(this)); // should reduce totalAssets so it becomes
    // below totalSupply
    console.log("After borrow: totalAssets = %d totalSupply = %d",
        lender.totalAssets(), lender.totalSupply());
    // now try to mint
    uint256 userBalance = lender.balanceOf(address(this));
    lender.mint(999999, address(this));
    uint256 deltaBalance = lender.balanceOf(address(this)) - userBalance;
    console.log("mint(999999), actual minted = %d", deltaBalance);
    vm.clearMockedCalls();
}
```
Execution console:
[PASS] test_mintWrongShares() (gas: 572788)
Logs:
Before borrow: totalAssets = 1000000 totalSupply = 1000000
After borrow: totalAssets = 999999 totalSupply = 1000000
mint(999999), actual minted = 1000000

## Recommendation
Since it's impossible to always find assets amount which converts back exactly to a
given number of shares, the only way to fix the problem is to handle mint function
differently from deposit, so that the user is minted exact amount of shares, using
the rounded up amount of assets.

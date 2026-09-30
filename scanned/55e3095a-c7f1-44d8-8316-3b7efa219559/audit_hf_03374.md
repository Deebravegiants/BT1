# [M] `initializeClone`

## Summary
Severity: Medium
Contest weight: 0.7253
Dataset id: 18400
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an arithmetic rounding error in the clone initialization routine of a DeFi position contract. The function calculates the price of a cloned position as price = _mint * ONE_DEC18 / _coll, which in Solidity performs integer division and therefore rounds the result down to the nearest integer. When the mint amount and the collateral amount are not perfectly divisible, the computed price is slightly lower than the true rational price. The contract later validates the collateral by checking collateralReserve * atPrice >= minted * ONE_DEC18 in checkCollateral(). Because the rounded‑down price is smaller, the left‑hand side of the inequality can become smaller than the right‑hand side by exactly one unit of the fixed‑point base, causing the require to fail and the transaction to revert with InsufficientCollateral. This situation occurs only during the clonePosition operation, when the caller supplies arbitrary initial collateral and mint values that are not cleanly divisible. Users attempting to clone an existing position therefore see the transaction revert, receive no new position, and their token balances remain unchanged, which is contrary to the expectation that cloning should succeed with the same economic parameters as the original. The issue was discovered during a manual audit and reproduced with a test that deliberately used non‑divisible values (e.g., 1000e18 mint and 1001 collateral), causing the price to round down to 0.999…e18 and triggering the revert. The bug is subtle because the rounding loss is only a single unit of the 18‑decimal fixed‑point representation, making the price appear correct when printed, and the failure only manifests in the internal collateral check, not in any external view. The impact is a denial‑of‑service style failure: legitimate users cannot clone positions unless they carefully choose divisible amounts, and an attacker could deliberately craft values that cause the rounding error, preventing clones and potentially forcing users to adjust their parameters. The root cause is the use of integer division without handling the remainder. The recommended fix is to adjust the price calculation to round up when a remainder exists, for example by adding one unit if _mint * ONE_DEC18 % _coll != 0, ensuring that the price is never lower than the exact rational value and that the collateral check cannot under‑flow. This change restores the intended business logic that the collateral supplied must be sufficient for the minted amount, eliminates the unexpected revert, and aligns the contract’s accounting with the protocol’s expectations.

## Proof of Concept
When cloning a position, `_initialCollateral` and `_initialMint` are used to calculate the `price` of the clone position.

The code is as follows:
    
```solidity
function initializeClone(address owner, uint256 _price, uint256 _limit, uint256 _coll, uint256 _mint) external onlyHub {
    if(_coll < minimumCollateral) revert InsufficientCollateral();
    setOwner(owner);
    
    price = _mint * ONE_DEC18 / _coll;   // <---------- use round down

    if (price > _price) revert InsufficientCollateral();
    limit = _limit;
    mintInternal(owner, _mint, _coll);

    emit PositionOpened(owner, original, address(zchf), address(collateral), _price);
}
```

1. The price calculation formula `price = _mint * ONE_DEC18 / _coll`, uses `round down`.
2. In the next step `mintInternal()` will execute mint, and internally will call `checkCollateral()`.

```solidity
function checkCollateral(uint256 collateralReserve, uint256 atPrice) internal view {
    if (collateralReserve * atPrice < minted * ONE_DEC18) revert InsufficientCollateral();
}
```

`checkCollateral()` will check `collateralReserve * atPrice < minted * ONE_DEC18`.

This has a problem: when calculating the price and there is a precision loss in price (round down), then `checkCollateral()` will definitely revert.

Because if precision loss occurs, `collateralReserve * atPrice` will be 1 less than `minted * ONE_DEC18`.

For example:

_initialCollateral = 101e18;  
_initialMint = 100e18;

Due to round down, price = 0.99e18.

Then `checkCollateral()` will revert because `101e18 * 0.99e18 < 100e18 * 1e18`.

Here is the demo code:

Will revert `InsufficientCollateral` in `checkCollateral()`  
Add to `GeneralTest.t.sol`

```solidity
function testCloneRevert() external {

    // 0.get 1000 for open bad position
    alice.obtainFrankencoins(swap, 1000 ether);
    col.mint(address(alice), 1001);  

    // 1. open new position
    vm.startPrank(address(alice));
    col.approve(address(hub), 1001);
    uint256 oldPrice = 1 * (10 ** 36);
    Position pos = Position(hub.openPosition(address(col), 100, 1001, 1000000 ether, 100 days, 1 days, 25000, oldPrice, 200000));        
    skip(7 * 86_400 + 60);

    console.log("0.pos price:",pos.price());

    // 2.pass _initialMint  _initialCollateral ,  will  round down
    uint256 _initialCollateral = 1001;
    uint256 _initialMint = 1000 * 10**18;

    uint256 newPrice = _initialMint * 10**18 / _initialCollateral;

    console.log("1.new price:",newPrice);
    console.log("1.new price Bigger than old?:",newPrice > oldPrice);

    col.mint(address(alice), _initialCollateral);
    col.approve(address(hub), _initialCollateral);

    // 3. clonePosition will revert ,  Although the parameters are all legal
    hub.clonePosition(address(pos),_initialCollateral , _initialMint);
    vm.stopPrank();
}
```

```bash
$ forge test --match testCloneRevert -vvv

Running 1 test for test/GeneralTest.t.sol:GeneralTest
[FAIL. Reason: InsufficientCollateral()] testCloneRevert() (gas: 2230875)
Logs:
  0.pos price: 1000000000000000000000000000000000000
  1.new price: 999000999000999000999000999000999000
  1.new price Bigger than old?: false

Traces:
  [2131375] GeneralTest::testCloneRevert() 
```

It is recommended to use round up.

## Recommendation
```solidity
function initializeClone(address owner, uint256 _price, uint256 _limit, uint256 _coll, uint256 _mint) external onlyHub {
    ...
    
    price = _mint * ONE_DEC18 / _coll;
    
    // Add this line to round up if not perfectly divisible
    if (price * _coll != _mint * ONE_DEC18) price += 1; // round up, avoid mintInternal() revert InsufficientCollateral
```

Impact seems insignificant  
Rounding down just means the price will decrease by a small percentage. Changing this to rounding up might cause a different edge case where an attacker can slightly increase the price by rounding.

Seems correct. Sponsor review requested.

Yes, I can confirm this issue. It doesn’t do much harm, but can cause some inconvenience when interacting with the protocol as it only works properly with cleanly divisible amounts for “mint” and “collateral”.

# [H] Assimilators should implement an interface

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The Assimilators are one of the core components within the application. They are used to move the tokens and can be thought of as a "middleware" between the Shell Protocol application and any other supported tokens.

The methods attached to the assimilators are called throughout the application and they are a critical component of the whole system. Because of this fact, it is extremely important that they behave correctly. 

A suggestion to restrict the possibility of errors when implementing them and when using them is to make all of the assimilators implement a unique specific interface. This way, any deviation would be immediately observed, right when the compilation happens.

#### Examples

Consider this example. The user calls `swapByOrigin`.


**src/Loihi.sol:L85-L89**
```solidity
function swapByOrigin (address _o, address _t, uint256 _oAmt, uint256 _mTAmt, uint256 _dline) public notFrozen returns (uint256 tAmt_) {

    return transferByOrigin(_o, _t, _dline, _mTAmt, _oAmt, msg.sender);

}
```

Which calls `transferByOrigin`. In `transferByOrigin`, if the origin index matches the target index, a different execution branch is activated.


**src/Loihi.sol:L187**
```solidity
if (_o.ix == _t.ix) return _t.addr.outputNumeraire(_rcpnt, _o.addr.intakeRaw(_oAmt));
```

In this case we need the output of `_o.addr.intakeRaw(_oAmt)`.

If we pick a random assimilator and check the implementation, we see the function `intakeRaw` needs to return the transferred amount.


**src/assimilators/mainnet/daiReserves/mainnetCDaiToDaiAssimilator.sol:L52-L67**
```solidity
// takes raw cdai amount, transfers it in, calculates corresponding numeraire amount and returns it
function intakeRaw (uint256 _amount) public returns (int128 amount_) {

    bool success = cdai.transferFrom(msg.sender, address(this), _amount);

    if (!success) revert("CDai/transferFrom-failed");

    uint256 _rate = cdai.exchangeRateStored();

    _amount = ( _amount * _rate ) / 1e18;

    cdai.redeemUnderlying(_amount);

    amount_ = _amount.divu(1e18);

}
```

However, with other implementations, the returns do not match. In the case of `MainnetDaiToDaiAssimilator`, it returns 2 values, which will make the `Loihi` contract work in this case but can misbehave in other cases, or even fail.


**src/assimilators/mainnet/daiReserves/mainnetDaiToDaiAssimilator.sol:L42-L49**
```solidity
// transfers raw amonut of dai in, wraps it in cDai, returns numeraire amount
function intakeRaw (uint256 _amount) public returns (int128 amount_, int128 balance_) {

    dai.transferFrom(msg.sender, address(this), _amount);

    amount_ = _amount.divu(1e18);

}
```

Making all the assimilators implement one unique interface will enforce the functions to look the same from the outside.

#### Recommendation

Create a unique interface for the assimilators and make all the contracts implement that interface.

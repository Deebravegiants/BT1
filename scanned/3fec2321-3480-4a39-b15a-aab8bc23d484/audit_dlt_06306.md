# [M] A deployed vault can be deployed again.

## Summary
Severity: Medium
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-04
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/80
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x08845b1c7713d61ed63e6b4b5abbcbb128841c5beee32489382a954d6241c4a7
**Severity:** medium

**Description:**
**Description**\
A deployed vault can be deployed again. This is due to a lack of validation to verify that the vault about to be deployed hasn't already been deployed before deploying it.
This will lead to duplicate vaults.

**Attack Scenario**\
An adversary can exploit the vulnerability to create bad duplicates of an already exisiting good vault in order to tarnsih the vault's reputation. It can also be done to trick users into interacting with bad vaults.

**Proof of Concept (PoC) File**

Add this test to DeployVault.t.sol and run forge test --mt test_deploy_twice
```
    function test_deploy_twice(uint16[2] memory weights_) external {
        vm.assume(weights_[0] > 0);
        vm.assume(weights_[1] > 0);
        address[] memory tokens = getTokens(2);

        uint256[] memory init_balances = new uint256[](2);
        init_balances[0] = 10000 * 10**18;
        init_balances[1] = 5000 * 10**18;

        uint256[] memory weights = new uint256[](2);
        weights[0] = uint256(weights_[0]);
        weights[1] = uint256(weights_[1]);

        approveTokens(address(catFactory), tokens, init_balances);
        t_deploy_volatile(tokens, init_balances, weights);

        approveTokens(address(catFactory), tokens, init_balances);
        t_deploy_volatile(tokens, init_balances, weights); // deploying the same vault again
    }
```
Poc file attached below.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/80_

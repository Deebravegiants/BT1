# [H] ready() is not Enough to Assume The Vault is Safe

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-02
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/77
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xb400710df222077848b27e5e57f5b13cd189bd8c4debe32dd8e4d54c38515881
**Severity:** high

**Description:**
**Description**\
"setupMaster" can call 2 functions: "setConnection()" and "finishSetup()". setConnection() connect vaults to create pools. finishSetup() take away setupMaster role hence no new vaults can be connected to pools. As we can see from ready() function, in order for vault to be assumed safe, setupMaster should call finishSetup():
```solidity
    /**
     * @notice Gives up short-term ownership of the vault. This makes the vault unstoppable.
     * @dev This function should ALWAYS be called before other liquidity providers deposit liquidity.
     * While it is not recommended, the escrow should ensure it is relativly safe trading through it (assuming a minimum output is set).
     */
    function finishSetup() external override {
        require(msg.sender == _setupMaster); // dev: No auth

        _setupMaster = address(0);

        emit FinishSetup();
    }

    /**
     * @notice View function to signal if a vault is safe to use.
     * @dev Checks if the setup master has been set to ZERO_ADDRESS.
     * In other words, has finishSetup been called?
     */
    function ready() external view override returns (bool) {
        // _setupMaster == address(0) ensures the pool is safe. The setup master can drain the pool!
        // _tokenIndexing[0] != address(0) check if the pool has been initialized correctly.
        // The additional check is there to ensure that the initial deployment returns false. 
        return _setupMaster == address(0) && _tokenIndexing[0] != address(0);
    }
```
Why this is so important? Because setupMaster can drain the pool as mentioned by NatSpec. It can create malicious vaults with malicious tokens and connect them to benign vault and steal the funds from users if users use the vault before finishSetup() called. 

What I will argue next is that this is not enough.


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/77_

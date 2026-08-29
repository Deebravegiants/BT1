# [M] Centralisation Risk: Admin Role of `TokenManagerEth` can Rug Pull All Eth from the Bridge

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-skale
Published: 2022-03-02
Source: https://github.com/code-423n4/2022-02-skale-findings/issues/35
Type: code-finding

## Details
# Lines of code

https://github.com/skalenetwork/ima-c4-audit/blob/main/contracts/schain/TokenManagers/TokenManagerEth.sol#L45-L49


# Vulnerability details

## Impact

There is a Centralisation risk of the bridge where the `DEFAULT_ADMIN_ROLE` of `TokenManagerEth.sol` is able to modify the ERC20 token on the SChain to any arbitrary address. This would allow the admin role to change the address to one where they have infinite supply, they could then call `exitToMain(amount)` equal to the balance of the DepositBox in the main Ethereum chain. After the message is process on the main Ethereum chain they will receive the entire Eth balance of that contract.

The rug pull attack occurs because there is a `DEFAULT_ADMIN_ROLE` which is set in the intiialisation to the `msg.sender` as seen in `initializeTokenManager()` below.

The `DEFAULT_ADMIN_ROLE` may then call `setEthErc20Address(IEthErc20 newEthErc20Address)`  setting `newEthErc20Address` to any arbitrary contract they control.


## Proof of Concept

```
    function setEthErc20Address(IEthErc20 newEthErc20Address) external override {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Not authorized caller");
        require(ethErc20 != newEthErc20Address, "Must be new address");
        ethErc20 = newEthErc20Address;
    }
```

```
    function initializeTokenManager(
        string memory newSchainName,
        IMessageProxyForSchain newMessageProxy,
        ITokenManagerLinker newIMALinker,
        ICommunityLocker newCommunityLocker,
        address newDepositBox
    )
        public
        virtual
        initializer
    {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-02-skale-findings/issues/35_

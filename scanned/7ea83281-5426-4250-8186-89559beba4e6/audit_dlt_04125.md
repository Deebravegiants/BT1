# [H] A buyout is paid by liquidity providers, not by a borrower

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/269
Type: sherlock-finding

## Details
Jeiwan

high

# A buyout is paid by liquidity providers, not by a borrower

## Summary
A buyout is paid by liquidity providers, not by a borrower
## Vulnerability Detail
A borrower is allowed to buy out their lien to apply new loan terms to it ([VaultImplementation.sol#L280](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/VaultImplementation.sol#L280)). To buy out a lien, the full lien's debt must be paid ([LienToken.sol#L143-L148](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/LienToken.sol#L143-L148)). However, when buying out via the vault contract, it's the vault that pays the buyout:
1. Vault calls `buyoutLien` on the LienToken contract ([VaultImplementation.sol#L301-L303](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/VaultImplementation.sol#L301-L303)):
    ```solidity
    IAstariaRouter(ROUTER()).LIEN_TOKEN().buyoutLien(
      ILienBase.LienActionBuyout(incomingTerms, position, recipient())
    );
    ```
1. And the LienToken contract transfers the buyout amount from `msg.sender`, i.e. the vault ([LienToken.sol#L143-L148](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/LienToken.sol#L143-L148)):
    ```solidity
    TRANSFER_PROXY.tokenTransferFrom(
      WETH,
      address(msg.sender), // @audit repaid by vault when called from a vault
      getPayee(lienId),
      uint256(buyout)
    );
    ```
1. Before making the call, the vault checks if it has enough tokens–these tokens belong to liquidity providers ([VaultImplementation.sol#L290-L293](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/VaultImplementation.sol#L290-L293)):
    ```solidity
    require(
      buyout <= ERC20(underlying()).balanceOf(address(this)),
      "not enough balance to buy out loan"
    );
    ```
1. The vault also approves spending to LienToken ([VaultImplementation.sol#L297-L300](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/VaultImplementation.sol#L297-L300)):
    ```solidity
    ERC20(underlying()).safeApprove(
      address(IAstariaRouter(ROUTER()).TRANSFER_PROXY()),
      buyout
    );
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/269_

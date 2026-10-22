# [M] _saleState check can be bypassed in Presale contract

## Summary
Severity: Medium
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-04
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/23
Type: hats-finding

## Details
**Github username:** @JeffCX
**Submission hash (on-chain):** 0x36354c97d8241dec945aa6679eb21d7598d3e2498421080cf934feaf661d5f93
**Severity:** medium

**Description:**
**Description**\

_saleState check can be bypassed in Presale contract

**Attack Scenario**\

In PresaleCvg.sol contract when calling investMint

we are validating if the sales start and if the sales finish in this [line of code](https://github.com/Cvg-Finance/hats-audit/blob/da48577d2f42fa8c2e35bb7223208ea6ba88012e/contracts/PresaleVesting/WlPresaleCvg.sol#L171)

```solidity
    function investMint(bytes32[] calldata _merkleProof, uint256 _amount, bool _isDai, uint256 _type) external {
        SaleState _saleState = saleState;

        require(_saleState > SaleState.NOT_ACTIVE, "PRESALE_NOT_STARTED");
        require(_saleState < SaleState.OVER, "PRESALE_ROUND_FINISHED");
```

However, there is no such check in the function [refillToken](https://github.com/Cvg-Finance/hats-audit/blob/da48577d2f42fa8c2e35bb7223208ea6ba88012e/contracts/PresaleVesting/WlPresaleCvg.sol#L216)

this means the token and sales amount can be refilled and updated even after the sale finishes which is not to other user that faithfully compete the sales

**Attachments**

1. **Proof of Concept (PoC) File**

user can just investMint with a tiny amout and refillToken even after the sales finishes

2. **Revised Code File (Optional)**

validate sales state in the function reillTOken as well

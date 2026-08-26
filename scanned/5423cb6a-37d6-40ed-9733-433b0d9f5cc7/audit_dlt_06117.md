# [?] Technically can sweep out LP tokens since those are ERC4626 for AURA (low severity)

## Summary
Severity: Unknown
Chain: Smart contract
Component: VMEX
Published: 2023-07-25
Source: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/5
Type: hats-finding

## Details
**Communication channel:** GalloDaSballo (discord)

**Description**\
Rescue Rewards doesn't protect the Staked Tokens, such as the ERC4626 tokenized Deposits from Aura

**Attack Scenario**\

This requires the admin to sweep out the funds, so it's just a QA finding

**Attachments**

1. **Proof of Concept (PoC) File**
```solidity
  function rescueRewardTokens(IERC20 reward, address receiver) external onlyGlobalAdmin {
    reward.safeTransfer(receiver, reward.balanceOf(address(this)));
  }
```

Allows to sweep tokens that represent the AURA deposits
##

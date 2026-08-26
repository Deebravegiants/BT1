# [M] Incompatibility With Rebasing/Deflationary/Inflationary tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: Metrom
Published: 2024-05-20
Source: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/4
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x49dc91be7d105d0afdf1d1de7368e3674aee43ff04a0a95efa91650b94ca46c0
**Severity:** medium

**Description:**
**Description**\
As mentioend by sponsers any ERC 20 is allowed, the Metrom contracts do not appear to support rebasing/deflationary/inflationary tokens whose balance changes during transfers or over time. 
Some tokens may make arbitrary balance modifications outside of transfers (e.g. Ampleforth style rebasing tokens, Compound style airdrops of governance tokens, mintable/burnable tokens). for example user creat Campaign and transfers 1000 tokens intor contract, the issue here that after sometime the tokens could decrease or increase.

**Attack Scenario**\
A user wants to create a campaign and uses [rebasing](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#balance-modifications-outside-of-transfers-rebasingairdrops) tokens, setting the amount as 1000. The 1000 tokens are transferred, but after sometime the balance will change, leading to potential reverts when `_processRewardClaim` is called.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Make sure for any rebasing/inflation/deflation tokens, Add support in contracts for such tokens before accepting user-supplied tokens.

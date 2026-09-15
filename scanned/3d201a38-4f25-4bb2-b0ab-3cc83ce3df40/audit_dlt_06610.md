# [M] depositWithSignature() function can be affected by DOS

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-09
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/63
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x65db4f9773c0e4f7ecce60decd9cb1711a85e625ffec2b6bf429a25b1954497d
**Severity:** medium

**Description:**
### Title
`depositWithSignature(()` function can be affected by DOS

### Severity
Medium

### Affected contracts
wrstMTRG.sol, wstARB.sol, wstDOJ.sol, wstMANTA.sol, wstMETIS.sol, wstROSE.sol, wstVLX.sol, wstZETA.sol and wstToken.sol

### Vulnerability Detail
In `wstToken.sol` `depositWithSignature(()` function is used to deposit the assets via permit in single transaction. 

```solidity
    function depositWithSignature(
        uint256 assets,
        address receiver,
        uint256 deadline,
        bool approveMax,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external nonReentrant returns (uint256 shares) {
        uint256 amount = approveMax ? type(uint256).max : assets;
@>        asset.permit(msg.sender, address(this), amount, deadline, v, r, s);
        return (deposit(assets, receiver));
    }
```
The issue is that while the transactions for depositWithSignature() function is in mempool, anyone could extract the signature parameters from the call to front-run the transaction with direct permit call.

This issue is originally submitted by Trust security aka Trust to various on chain protocols and the issue is confirmed by reputed protocols like Open Zeppelin, AAVE, The Graph, Uniswap-V2.

To understand the issue in detail, Please refer below link:

link: https://www.trust-security.xyz/post/permission-denied

> An attacker can extract the signature by observing the mempool, front-run the victim with a direct permit, and revert the function call for the user. "In the case that there is no fallback code path the DOS is long-term (there are bypasses through flashbots in some chains, but that's a really bad scenario to resort to)." as stated by Trust Security.

This issue would indeed increase the approval for the user if the front-run got successful. But as the permit has already been used, the call to either of above permit functions will revert making whole transaction revert. Thus making the victim not able to make successful call to either of above permit functions to carry out borrow repay or stake or member registration.

Consider a normal scenario,

1) Bob wants to deposit stROSE with permit so he calls wstROSE.depositWithSignature() function.

2) Alice observes the transactions in mempool and extract the signature parameters from the call to front-run the transaction with direct permit call. Alice transaction got successful due to high gas fee paid by her to miner by front running the Bob's transaction.

3) This action by Alice would indeed increase the approval for the Bob since the front-run got successful.

4) But as the permit is already been used by Alice so the call to wstROSE.depositWithSignature() will revert making whole transaction revert.

5) Now, Bob will not able to make successful call to wstROSE.depositWithSignature() function to deposit stROSE by using ERC20 permit(). 

This is due to griefing attack by Alice. She will keep repeating such attack as the intent is to grief the protocol users.

### Impact
Users will not be able to use the permit functions for asset deposit via `depositWithSignature()` function so these function would be practically unusable and users functionality would be affected due to above described issue.

### Recommendation to fix
Wrap the permit calls in a `try catch` block in above functions using permit().

For example:

```diff
    function depositWithSignature(
        uint256 assets,
        address receiver,
        uint256 deadline,
        bool approveMax,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external nonReentrant returns (uint256 shares) {
        uint256 amount = approveMax ? type(uint256).max : assets;
-        asset.permit(msg.sender, address(this), amount, deadline, v, r, s);
-         return (deposit(assets, receiver));
+       try asset.permit(msg.sender, address(this), amount, deadline, v, r, s) {
+            return (deposit(assets, receiver));
+       }
+       catch {
+           if (asset.allowance(msg.sender, address(this)) >=  amount) {
+                   return (deposit(assets, receiver));
+           } else {
+                   revert("PermitFailed");
+       }
    }
```

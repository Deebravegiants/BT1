# [M] Attacker can temporary deplete available redemption/issuance by running issuance then redemption or vice versa

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-02-reserve-mitigation-contest
Published: 2023-02-17
Source: https://github.com/code-423n4/2023-02-reserve-mitigation-contest-findings/issues/79
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/610cfca553beea41b9508abbfbf4ee4ce16cbc12/contracts/libraries/Throttle.sol#L66-L75


# Vulnerability details

## Impact
Attacker can deplete available issuance or redemption by first issuing and then redeeming in the same tx or vice versa.
The available redemption/issuance will eventually grow back, but this temporary reduces the available amount.
This can also use to front run other user who tries to redeem/issue in order to fail their tx. 

## Proof of Concept
In the PoC below a user is able to reduce the redemption available by more than 99% (1e20 to 1e14), and that's without spending anything but gas (they end up with the same amount of RToken as before)



```diff
diff --git a/test/RToken.test.ts b/test/RToken.test.ts
index e04f51db..33044b79 100644
--- a/test/RToken.test.ts
+++ b/test/RToken.test.ts
@@ -1293,6 +1293,31 @@ describe(`RTokenP${IMPLEMENTATION} contract`, () => {
           )
         })
 
+        it('PoC', async function () {
+          const rechargePerBlock = config.issuanceThrottle.amtRate.div(BLOCKS_PER_HOUR);
+
+          advanceTime(60*60*5);
+
+          let totalSupply =  await rToken.totalSupply();
+          let redemptionAvailable = await rToken.redemptionAvailable();
+          let issuanceAvailable = await rToken.issuanceAvailable();
+
+          console.log({redemptionAvailable, issuanceAvailable, totalSupply});
+
+          let toIssue = redemptionAvailable.mul(111111n).div(100000n);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-02-reserve-mitigation-contest-findings/issues/79_

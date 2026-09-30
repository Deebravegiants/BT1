# [?] SECURITY.md: Require exploit PoC for submission consideration (#31113)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-04-12
Source: https://github.com/solana-labs/solana/commit/7f7351d7638e6a7624be22f35112c604e61b30a2
Type: security-commit

## Details
SECURITY.md: Require exploit PoC for submission consideration (#31113)

## Patch
### SECURITY.md
```diff
@@ -10,7 +10,9 @@
 **DO NOT CREATE A GITHUB ISSUE** to report a security problem.
 
 Instead please use this [Report a Vulnerability](https://github.com/solana-labs/solana/security/advisories/new) link.
-Provide a helpful title and detailed description of the problem.
+Provide a helpful title, detailed description of the vulnerability and an exploit
+proof-of-concept. Speculative submissions without proof-of-concept will be closed
+with no further consideration.
 
 If you haven't done so already, please **enable two-factor auth** in your GitHub account.
 
@@ -73,7 +75,8 @@ Since the software version will not change after the patch is applied, request t
 Once the fix has been deployed to the security group validators, the patches from the security advisory may be merged into the main source repository. A new official release for each affected branch should be shipped and all validators requested to upgrade as quickly as possible.
 
 ### 7. Security Advisory Bounty Accounting and Cleanup
-If this issue is eligible for a bounty, prefix the title of the security advisory with one of the following, depending on the severity:
+If this issue is [eligible](#eligibility) for a bounty, prefix the title of the
+security advisory with one of the following, depending on the severity:
 - [Bounty Category: Critical: Loss of Funds]
 - [Bounty Category: Critical: Consensus / Safety Violations]
 - [Bounty Category: Critical: Liveness / Loss of Availability]
@@ -132,8 +135,9 @@ The following components are out of scope for the bounty program
 to, any and all web properties not explicitly listed on this page)
 
 ### Eligibility:
+* Submissions _MUST_ include an exploit proof-of-concept to be considered eligible
 * The participant submitting the bug report shall follow the process outlined within this document
-* Valid exploits can be eligible even if they are not successfully executed on the cluster
+* Valid exploits can be eligible even if they are not successfully executed on a public cluster
 * Multiple submissions for the same class of exploit are still eligible for compensation, though may be compensated at a lower rate, however these will be assessed on a case-by-case basis
 * Participants must complete KYC and sign the participation agreement here when the registrations are open https://solana.foundation/kyc. Security exploits will still be assessed and open for submission at all times. This needs only be done prior to distribution of tokens.
 
```

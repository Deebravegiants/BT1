# [?] chore: revise vulnerability disclosure process in SECURITY.md (#10516)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-06-19
Source: https://github.com/dfinity/ic/commit/ffdcdbe45c9167a28c25ce646840ee883cb6ff35
Type: security-commit

## Details
chore: revise vulnerability disclosure process in SECURITY.md (#10516)

Updates the section on how to report a vulnerability by removing the
securitybugs@dfinity.org mail address.

## Patch
### SECURITY.md
```diff
@@ -11,13 +11,8 @@ We appreciate your help in keeping our projects secure.
 If you believe you have found a security vulnerability in any of our repositories, please report it responsibly to us as described below:
 
 1. **Do not disclose the vulnerability publicly.** Public disclosure could be exploited by attackers before it can be fixed.
-2. **Ideally, disclose the vulnerability through [Hackenproof](https://hackenproof.com/programs/internet-computer-protocol)**
+2. **Disclose the vulnerability through [Hackenproof](https://hackenproof.com/programs/internet-computer-protocol)**
     * Hackenproof facilitates disclosure and streamlines Bugbounty payouts.
-4. **Alternatively, send an email to securitybugs@dfinity.org.** Please include the following information in your email:
-    * A description of the vulnerability
-    * Steps to reproduce the vulnerability
-    * Risk rating of the vulnerability
-    * Any other relevant information
 
 We will respond to your report within 72 hours and work with you to fix the vulnerability as soon as possible.
 
```

# [M] 5.1 Unkill Function Allows Claiming After Closing

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 2 Risk Accepted

Function unKill(), only callable by the PlatformFactory contract owner, allows to reset isKilled
to false. If a bribe manager calls closeBribe() while the Platform is killed, and the platform is then
unkilled, the bribe becomes claimable again, even though the left over funds have been transferred by
closeBribe(). Users can claim their bribes and the funds will be taken from other bribes sharing the
same tokens.

Risk accepted

StakeDao accepts the risk but already fixed the issue by removing the unkill function in the latest code
version that was not included in the audit.

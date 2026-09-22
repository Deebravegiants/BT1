# [C] CVE-2021-46250

## Summary
Severity: Critical
Advisory: CVE-2021-46250
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-15
Source: https://osv.dev/vulnerability/CVE-2021-46250
Type: osv

## Details
An issue in SOA2Login::commented of ScratchOAuth2 before commit a91879bd58fa83b09283c0708a1864cdf067c64a allows attackers to authenticate as other users on downstream components that rely on ScratchOAuth2.

## References
- https://github.com/ScratchVerifier/ScratchOAuth2/commit/a91879bd58fa83b09283c0708a1864cdf067c64a

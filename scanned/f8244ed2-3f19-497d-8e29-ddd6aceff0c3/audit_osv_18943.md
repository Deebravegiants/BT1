# [H] CVE-2020-5242

## Summary
Severity: High
Advisory: CVE-2020-5242
Aliases: GHSA-w698-693g-23hv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-20
Source: https://osv.dev/vulnerability/CVE-2020-5242
Type: osv

## Details
openHAB before 2.5.2 allow a remote attacker to use REST calls to install the EXEC binding or EXEC transformation service and execute arbitrary commands on the system with the privileges of the user running openHAB. Starting with version 2.5.2 all commands need to be whitelisted in a local file which cannot be changed via REST calls.

## References
- https://github.com/openhab/openhab-addons/security/advisories/GHSA-w698-693g-23hv
- https://github.com/openhab/openhab-addons/commit/4c4cb664f2e2c3866aadf117d22fb54aa8dd0031

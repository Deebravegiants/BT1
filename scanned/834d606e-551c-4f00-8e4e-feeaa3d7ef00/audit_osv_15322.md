# [M] CVE-2019-15508

## Summary
Severity: Medium
Advisory: CVE-2019-15508
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-23
Source: https://osv.dev/vulnerability/CVE-2019-15508
Type: osv

## Details
In Octopus Tentacle versions 3.0.8 to 5.0.0, when a web request proxy is configured, an authenticated user (in certain limited OctopusPrintVariables circumstances) could trigger a deployment that writes the web request proxy password to the deployment log in cleartext. This is fixed in 5.0.1. The fix was back-ported to 4.0.7.

## References
- https://github.com/OctopusDeploy/Issues/issues/5750

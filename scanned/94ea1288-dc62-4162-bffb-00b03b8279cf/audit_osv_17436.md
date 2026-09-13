# [H] CVE-2020-15167

## Summary
Severity: High
Advisory: CVE-2020-15167
Aliases: GHSA-mw2v-4q78-j2cw
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-09-02
Source: https://osv.dev/vulnerability/CVE-2020-15167
Type: osv

## Details
In Miller (command line utility) using the configuration file support introduced in version 5.9.0, it is possible for an attacker to cause Miller to run arbitrary code by placing a malicious `.mlrrc` file in the working directory. See linked GitHub Security Advisory for complete details. A fix is ready and will be released as Miller 5.9.1.

## References
- https://github.com/johnkerl/miller/security/advisories/GHSA-mw2v-4q78-j2cw

# [H] CVE-2021-43307

## Summary
Severity: High
Advisory: CVE-2021-43307
Aliases: GHSA-4x5v-gmq8-25ch
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2021-43307
Type: osv

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the semver-regex npm package, when an attacker is able to supply arbitrary input to the test() method

## References
- https://research.jfrog.com/vulnerabilities/semver-regex-redos-xray-211349/

# [H] Malicious takeover of previously owned ENS names

## Summary
Severity: High
Advisory: GHSA-8f9f-pc5v-9r5h
CVE: CVE-2020-5232
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-8f9f-pc5v-9r5h
Type: github-advisory

## Affected
- npm: `@ensdomains/ens` — affected >=0 <0.4.0

## Details
### Impact
A user who owns an ENS domain can set a "trapdoor", allowing them to transfer ownership to another user, and later regain ownership without the new owner's consent or awareness.

### Patches

A new ENS deployment is being rolled out that fixes this vulnerability in the ENS registry. The registry is newly deployed at [0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e](https://etherscan.io/address/0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e).

### Workarounds
Do not accept transfers of ENS domains from other users on the old registrar.

## References
- https://github.com/ensdomains/ens/security/advisories/GHSA-8f9f-pc5v-9r5h
- https://nvd.nist.gov/vuln/detail/CVE-2020-5232
- https://github.com/ensdomains/ens/commit/36e10e71fcddcade88646821e0a57cc6c19e1ecf

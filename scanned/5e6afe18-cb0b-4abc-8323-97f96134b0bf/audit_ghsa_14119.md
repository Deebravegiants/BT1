# [M] vm2 vulnerable to Inspect Manipulation

## Summary
Severity: Medium
Advisory: GHSA-p5gc-c584-jj6v
CVE: CVE-2023-32313
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-17
Source: https://github.com/advisories/GHSA-p5gc-c584-jj6v
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.9.18

## Details
In versions 3.9.17 and lower of vm2 it was possible to get a read-write reference to the node `inspect` method and edit options for `console.log`.

### Impact
A threat actor can edit options for `console.log`.

### Patches
This vulnerability was patched in the release of version `3.9.18` of `vm2`.

### Workarounds
After creating a vm make the `inspect` method readonly with `vm.readonly(inspect)`.

### References
PoC - https://gist.github.com/arkark/c1c57eaf3e0a649af1a70c2b93b17550

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [VM2](https://github.com/patriksimek/vm2)

Thanks to @arkark (Takeshi Kaneko) of GMO Cybersecurity by Ierae, Inc. for disclosing this vulnerability.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-p5gc-c584-jj6v
- https://nvd.nist.gov/vuln/detail/CVE-2023-32313
- https://github.com/patriksimek/vm2/commit/5206ba25afd86ef547a2c9d48d46ca7a9e6ec238
- https://gist.github.com/arkark/c1c57eaf3e0a649af1a70c2b93b17550
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.9.18

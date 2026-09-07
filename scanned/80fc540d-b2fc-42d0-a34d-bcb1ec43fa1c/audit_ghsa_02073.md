# [M] Missing Handler in @scandipwa/magento-scripts

## Summary
Severity: Medium
Advisory: GHSA-52qp-gwwh-qrg4
CVE: CVE-2021-32684
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-52qp-gwwh-qrg4
Type: github-advisory

## Affected
- npm: `@scandipwa/magento-scripts` — affected >=1.5.1 <1.5.3

## Details
### Impact
After changing the function from synchronous to asynchronous there wasn't implemented handler in the [start](https://docs.create-magento-app.com/getting-started/available-commands/start), [stop](https://docs.create-magento-app.com/getting-started/available-commands/stop), [exec](https://docs.create-magento-app.com/getting-started/available-commands/exec) and [logs](https://docs.create-magento-app.com/getting-started/available-commands/logs) commands, effectively making them unusable.

### Patches
[Version 1.5.3](https://github.com/scandipwa/create-magento-app/releases/tag/%40scandipwa%2Fmagento-scripts%401.5.3) contains patches for the problems described above.

### Workarounds
Upgrade to patched or latest (recommended) version `npm i @scandipwa/magento-scripts@1.5.3` or `npm i @scandipwa/magento-scripts@latest`.

### References
New releases always available here: https://github.com/scandipwa/create-magento-app/releases

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [create-magento-app](https://github.com/scandipwa/create-magento-app/issues)

## References
- https://github.com/scandipwa/create-magento-app/security/advisories/GHSA-52qp-gwwh-qrg4
- https://nvd.nist.gov/vuln/detail/CVE-2021-32684
- https://github.com/scandipwa/create-magento-app/commit/89115db7031e181eb8fb4ec2822bc6cab88e7071

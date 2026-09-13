# [H] Denial of Service in soketi

## Summary
Severity: High
Advisory: GHSA-86ch-6w7v-v6xf
CVE: CVE-2022-21667
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-86ch-6w7v-v6xf
Type: github-advisory

## Affected
- npm: `@soketi/soketi` — affected >=0 <0.24.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

There was a wrong behavior when reading POST requests, making the server crash if it couldn't read the body. In case a POST request was sent to any endpoint of the server with an empty body, **even unauthenticated with the Pusher Protocol**, it would simply just crash the server for trying to send a response after the request closed.

All users that run the server are affected by it and it's highly recommended to upgrade to the latest patch.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Updating to at least 0.24.1 or the latest version.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

No. Upgrading is the only solution.

### References
_Are there any links users can visit to find out more?_

https://github.com/soketi/soketi/releases/tag/0.24.1

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the issues board](https://github.com/soketi/soketi/issues)
* Email us at [alex@renoki.org](mailto:alex@renoki.org)

## References
- https://github.com/soketi/soketi/security/advisories/GHSA-86ch-6w7v-v6xf
- https://nvd.nist.gov/vuln/detail/CVE-2022-21667
- https://github.com/soketi/soketi/commit/4b12efef9c31117c36a0a0f1c3aa32114e86364b
- https://github.com/soketi/soketi
- https://github.com/soketi/soketi/releases/tag/0.24.1

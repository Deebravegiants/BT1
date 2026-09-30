# [C] Authenticated RCE via unsanitized compression_algorithm

## Summary
Severity: Critical
Advisory: CVE-2026-28384
Aliases: GHSA-4rmf-rcp8-2r9g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-28384
Type: osv

## Details
An improper sanitization of the compression_algorithm parameter in Canonical LXD allows an authenticated, unprivileged user to execute commands as the LXD daemon on the LXD server via API calls to the image and backup endpoints. This issue affected LXD from 4.12 through 6.6 and was fixed in the snap versions 5.0.6-e49d9f4 (channel 5.0/stable), 5.21.4-1374f39 (channel 5.21/stable), and 6.7-1f11451 (channel 6.0 stable). The channel 4.0/stable is not affected as it contains version 4.0.10.

## References
- https://discourse.ubuntu.com/t/lxd-authenticated-remote-code-execution-fixes-available/78365
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28384.json
- https://github.com/canonical/lxd/security/advisories/GHSA-4rmf-rcp8-2r9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-28384
- https://github.com/canonical/lxd/commit/043696a13171ace7dd4c2b32d34ce039ab629052
- https://github.com/canonical/lxd/commit/7046979645c2ce1b63b2f9e60ddf6cbc4c4b78f9
- https://github.com/canonical/lxd/commit/b7b411caf5c4971bfe2386c72128f44d7e2aaf4f
- https://github.com/canonical/lxd

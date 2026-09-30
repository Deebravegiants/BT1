# [H] OpenTofu: Possible arbitrary file read during certain git operations via a maliciously crafted URL

## Summary
Severity: High
Advisory: GHSA-q7j3-v8qv-22vq
CWE: CWE-1395
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-q7j3-v8qv-22vq
Type: github-advisory

## Affected
- Go: `github.com/opentofu/opentofu` — affected >=0 <1.11.10
- Go: `github.com/opentofu/opentofu` — affected >=1.12.0-beta1 <1.12.3

## Details
### Impact
Possible data exposure.
#### Summary
While downloading packages from a maliciously crafted URL, some git operations against that URL could allow arbitrary file read.
This might allow disclosure of confidential information.

#### Details
OpenTofu relies on [go-getter](https://github.com/hashicorp/go-getter) for downloading packages like providers and modules. While doing so from a maliciously crafted URL, the operator could be affected by confidential information disclosure. 

The go-getter maintainers have recently published [CVE-2026-4660](https://github.com/advisories/GHSA-92mm-2pjq-r785) for this library which indirectly affects OpenTofu's behavior.

Typical use of OpenTofu already requires caution in selection of URLs that are used to download modules and providers.

### Patches
OpenTofu v1.11.10 and v1.12.3 address these vulnerabilities by upgrading to the [hashicorp/go-getter@v1.8.6](https://github.com/hashicorp/go-getter/releases/tag/v1.8.6) that fixes this vulnerability.

The OpenTofu v1.10 series is also impacted by these vulnerabilities. However, that series is built with an older version of the library and upgrading it risks breaking the whole v1.10 series. 
For those using OpenTofu v1.10 releases, we recommend planning an upgrade to OpenTofu v1.11.10 in the near future.

### References
* [Initial report](https://github.com/opentofu/opentofu/pull/4288)
* [CVE-2026-4660](https://github.com/advisories/GHSA-92mm-2pjq-r785)
* [OpenTofu v1.12 patch](https://github.com/opentofu/opentofu/pull/4293)
* [OpenTofu v1.11 patch](https://github.com/opentofu/opentofu/pull/4292)
* [Patched v1.12.3 version](https://github.com/opentofu/opentofu/releases/tag/v1.12.3)
* [Patched v1.11.10 version](https://github.com/opentofu/opentofu/releases/tag/v1.11.10)

## References
- https://github.com/opentofu/opentofu/security/advisories/GHSA-q7j3-v8qv-22vq
- https://github.com/opentofu/opentofu/pull/4288
- https://github.com/opentofu/opentofu/pull/4292
- https://github.com/opentofu/opentofu/pull/4293
- https://github.com/advisories/GHSA-92mm-2pjq-r785
- https://github.com/hashicorp/go-getter/releases/tag/v1.8.6
- https://github.com/opentofu/opentofu
- https://github.com/opentofu/opentofu/releases/tag/v1.11.10
- https://github.com/opentofu/opentofu/releases/tag/v1.12.3

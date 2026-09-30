# [H] containerd allows host filesystem access on pull

## Summary
Severity: High
Advisory: GHSA-cm76-qm8v-3j95
CVE: CVE-2025-47290
CWE: CWE-367
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:U (CVSS_V4)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-cm76-qm8v-3j95
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd/v2` — affected >=2.1.0 <2.1.1

## Details
### Impact

A time-of-check to time-of-use (TOCTOU) vulnerability was found in containerd v2.1.0. While unpacking an image during an image pull, specially crafted container images could arbitrarily modify the host file system. 

### Patches
This bug has been fixed in the following containerd versions:

* 2.1.1

The only affected version of containerd is 2.1.0.  Other versions of containerd are not affected.

Users should update to this version to resolve the issue.

### Workarounds
Ensure that only trusted images are used and that only trusted users have permissions to import images.

### Credits
The containerd project would like to thank Tõnis Tiigi for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md).

### References
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-47290

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:

* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-cm76-qm8v-3j95
- https://nvd.nist.gov/vuln/detail/CVE-2025-47290
- https://github.com/containerd/containerd/commit/cada13298fba85493badb6fecb6ccf80e49673cc
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v2.1.1

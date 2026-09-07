# [H] URL previews of unusual or maliciously-crafted pages can crash Synapse media repositories or Synapse monoliths

## Summary
Severity: High
Advisory: GHSA-22p3-qrh9-cx32
CVE: CVE-2022-31052
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-22p3-qrh9-cx32
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.61.1

## Details
### Impact

URL previews of some web pages can exhaust the available stack space for the Synapse process due to unbounded recursion.
This is sometimes recoverable and leads to an error for the request causing the problem, but in other cases the Synapse process may crash altogether.

It is possible to exploit this maliciously, either by malicious users on the homeserver, or by remote users sending URLs that a local user's client may automatically request a URL preview for.
Remote users are not able to exploit this directly, because [the URL preview endpoint is authenticated](https://spec.matrix.org/v1.2/client-server-api/#get_matrixmediav3preview_url).

### Am I affected?

* deployments with `url_preview_enabled: false` set in configuration are not affected.
* deployments with `url_preview_enabled: true` set in configuration **are** affected.
* deployments with no configuration value set for `url_preview_enabled` are not affected, because the default is `false`.

### Patches

Administrators of homeservers with URL previews enabled are advised to upgrade to v1.61.1 or higher.

### Workarounds

* URL previews can be disabled in the configuration file by setting `url_preview_enabled: false`.
* Deployments using workers can choose to offload URL previews to one or more dedicated worker(s), ensuring that a process crash does not disrupt other functionality of Synapse.

### For more information

If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-22p3-qrh9-cx32
- https://nvd.nist.gov/vuln/detail/CVE-2022-31052
- https://github.com/matrix-org/synapse/commit/fa1308061802ac7b7d20e954ba7372c5ac292333
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2022-224.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7EARKKJZ2W7WUITFDT4EG4NVATFYJQHF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QGSDQ4YAITCUACAB7SXQZDJIU3IQ4CJD
- https://spec.matrix.org/v1.2/client-server-api/#get_matrixmediav3preview_url

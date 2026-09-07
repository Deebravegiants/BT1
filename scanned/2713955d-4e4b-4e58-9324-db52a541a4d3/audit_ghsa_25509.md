# [M] Uncontrolled Resource Consumption in Matrix Synapse

## Summary
Severity: Medium
Advisory: GHSA-4822-jvwx-w47h
CVE: CVE-2022-41952
CWE: CWE-400, CWE-772
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-4822-jvwx-w47h
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.53.0

## Details
### Impact

Synapse before 1.52.0 with URL preview functionality enabled will attempt to generate URL previews for media stream URLs without properly limiting connection time. Connections will only be terminated after `max_spider_size` (default: 10M) bytes have been downloaded, which can in some cases lead to long-lived connections towards the streaming media server (for instance, Icecast).

This can cause excessive traffic and connections toward such servers if their stream URL is, for example, posted to a large room with many Synapse instances with URL preview enabled.

### Patches
1.52.0 implements a timeout mechanism which will terminate URL preview connections after 30 seconds. Since generating URL previews for media streams is not supported and always fails, 1.53.0 additionally implements an allow list for content types for which Synapse will even attempt to generate a URL preview.

We recommend upgrading to 1.53.0 to fully resolve the issue.

### Workarounds
Turn off URL preview functionality by setting `url_preview_enabled: false` in the Synapse configuration file.

### References
- Patch (timeout): https://github.com/matrix-org/synapse/pull/11784
- Patch (content type allow list): https://github.com/matrix-org/synapse/pull/11936

### For more information
If you have any questions or comments about this advisory, e-mail us at security@matrix.org.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-4822-jvwx-w47h
- https://nvd.nist.gov/vuln/detail/CVE-2022-41952
- https://github.com/matrix-org/synapse/pull/11784
- https://github.com/matrix-org/synapse/pull/11936
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.52.0
- https://github.com/matrix-org/synapse/releases/tag/v1.53.0

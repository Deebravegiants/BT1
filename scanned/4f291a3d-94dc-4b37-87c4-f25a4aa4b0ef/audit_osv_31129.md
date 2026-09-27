# [M] ASoC: SOF: Intel: hda-dai: Ensure DAI widget is valid during params

## Summary
Severity: Medium
Advisory: CVE-2024-58012
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58012
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: Intel: hda-dai: Ensure DAI widget is valid during params

Each cpu DAI should associate with a widget. However, the topology might
not create the right number of DAI widgets for aggregated amps. And it
will cause NULL pointer deference.
Check that the DAI widget associated with the CPU DAI is valid to prevent
NULL pointer deference due to missing DAI widgets in topologies with
aggregated amps.

## References
- https://git.kernel.org/stable/c/569922b82ca660f8b24e705f6cf674e6b1f99cc7
- https://git.kernel.org/stable/c/789a2fbf0900982788408d3b0034e0e3f914fb3b
- https://git.kernel.org/stable/c/e012a77e4d7632cf615ba9625b1600ed8985c3b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58012.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

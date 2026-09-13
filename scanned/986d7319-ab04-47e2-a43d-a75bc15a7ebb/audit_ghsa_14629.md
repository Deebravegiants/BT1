# [H] Synapse can be forced to thumbnail unexpected file formats, invoking external, potentially untrustworthy decoders

## Summary
Severity: High
Advisory: GHSA-vp6v-whfm-rv3g
CVE: CVE-2024-53863
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-vp6v-whfm-rv3g
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.120.1

## Details
### Impact

In Synapse versions before 1.120.1, enabling the `dynamic_thumbnails` option or processing a specially crafted request could trigger the decoding and thumbnail generation of uncommon image formats, potentially invoking external tools like Ghostscript for processing.

This significantly expands the attack surface in a historically vulnerable area, presenting a risk that far outweighs the benefit, particularly since these formats are rarely used on the open web or within the Matrix ecosystem.

For a list of image formats, as well as decoding libraries and helper programs used, see [the Pillow documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

### Patches

Synapse 1.120.1 addresses the issue by restricting thumbnail generation to images in the following widely used formats: PNG, JPEG, GIF, and WebP.

### Workarounds

- Ensure any image codecs and helper programs, such as Ghostscript, are patched against security vulnerabilities.
- Uninstall unused image decoder libraries and helper programs, such as Ghostscript, from the system environment that Synapse is running in.
    - Depending on the installation method, there may be some decoder libraries bundled with Pillow and these cannot be easily uninstalled.
    - The official Docker container image does not include Ghostscript.

### References

- [The Pillow documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) includes a list of supported image formats and which libraries or helper programs are used to decode them.

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-vp6v-whfm-rv3g
- https://nvd.nist.gov/vuln/detail/CVE-2024-53863
- https://github.com/element-hq/synapse

# [M] Syft improper temporary file cleanup

## Summary
Severity: Medium
Advisory: GHSA-rjcw-vg7j-m9rc
CVE: CVE-2026-33481
CWE: CWE-460
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-rjcw-vg7j-m9rc
Type: github-advisory

## Affected
- Go: `github.com/anchore/syft` — affected >=0 <1.42.3

## Details
### Impact
Syft versions before v1.42.3 would not properly cleanup temporary storage if the temporary storage was exhausted during a scan. When scanning archives Syft will unpack those archives into temporary storage then inspect the unpacked contents. Under normal operation Syft will remove the temporary data it writes after completing a scan.

This vulnerability would affect users of Syft that were scanning content that could cause Syft to fill the temporary storage that would then cause Syft to raise an error and exit. When the error is triggered Syft would exit without properly removing the temporary files in use. In our testing this was most easily reproduced by scanning very large artifacts or highly compressed artifacts such as a zipbomb.

Because Syft would not clean up its temporary files, the result would be filling temporary file storage preventing future runs of Syft or other system utilities that rely on temporary storage being available.

### Patches

The patch has been released in v1.42.3

Syft now cleans up temporary files when an error condition is encountered.

### Workarounds

There are no workarounds for this vulnerability in Syft. Users that find their temporary storage depleted can manually remove the temporary files.

## References
- https://github.com/anchore/syft/security/advisories/GHSA-rjcw-vg7j-m9rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33481
- https://github.com/anchore/stereoscope/pull/537
- https://github.com/anchore/syft/pull/4629
- https://github.com/anchore/syft/pull/4668
- https://github.com/anchore/syft

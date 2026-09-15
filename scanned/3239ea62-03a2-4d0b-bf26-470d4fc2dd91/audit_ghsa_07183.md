# [H] DIRAC: Pilot code downloaded over unverified HTTPS connection

## Summary
Severity: High
Advisory: GHSA-vg99-gr89-qhw9
CVE: CVE-2026-61668
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-vg99-gr89-qhw9
Type: github-advisory

## Affected
- PyPI: `DIRAC` — affected >=6.20.1 <8.0.79
- PyPI: `DIRAC` — affected >=8.1.0a1 <9.0.22
- PyPI: `DIRAC` — affected >=9.1.0 <9.1.10

## Details
### Summary
The second stage pilot (pilot.tar) is downloaded by the initial wrapper script without any verification of the webservers' SSL certificate and the contained script is subsequently executed. The checksum is tested, but the reference checksum file is downloaded over the same unvalidated channel.

### Details
The pilot wrapper downloads and executes the main second stage pilot script, but the SSL validation on this connection is explicitly disabled (to match old python < 2.7.9 behaviour):
https://github.com/DIRACGrid/DIRAC/blob/integration/src/DIRAC/WorkloadManagementSystem/Utilities/PilotWrapper.py#L292-L296

This means that the second stage pilot code is not verified in any way and could potentially be altered by a man-in-the-middle attack to execute arbitrary code in the pilot context (i.e. with access to the pilot proxy/credentials).

The HTTPS connection should be validated against both the system certificates and $X509_CERT_DIR and fail if neither validate correctly.

### Impact
This would require a man-in-the-middle style attack against a grid site's network (i.e. changing the DNS or routing to redirect the pilot's connection); this is likely to be difficult which probably limits the potential impact.

### Patched versions:
https://pypi.org/project/DIRAC/8.0.79/
https://pypi.org/project/DIRAC/9.0.22/
https://pypi.org/project/DIRAC/9.1.10/

## References
- https://github.com/DIRACGrid/DIRAC/security/advisories/GHSA-vg99-gr89-qhw9
- https://github.com/DIRACGrid/DIRAC
- https://pypi.org/project/DIRAC/8.0.79
- https://pypi.org/project/DIRAC/9.0.22
- https://pypi.org/project/DIRAC/9.1.10

# [H] When matrix-nio receives forwarded room keys, the receiver doesn't check if it requested the key from the forwarder

## Summary
Severity: High
Advisory: GHSA-w4pr-4vjg-hffh
CVE: CVE-2022-39254
CWE: CWE-287, CWE-322
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-w4pr-4vjg-hffh
Type: github-advisory

## Affected
- PyPI: `matrix-nio` — affected >=0 <0.20

## Details
When matrix-nio before 0.20 requests a room key from our devices, it correctly accepts key forwards only if they are a response to a previous request. However, it doesn't check that the device that responded matches the device the key was requested from.

This allows a malicious homeserver to insert room keys of questionable validity into the key store in some situations, potentially assisting in an impersonation attack.

### For more information
If you have any questions or comments about this advisory, e-mail us at [poljar@termina.org.uk](mailto:poljar@termina.org.uk).

## References
- https://github.com/poljar/matrix-nio/security/advisories/GHSA-w4pr-4vjg-hffh
- https://nvd.nist.gov/vuln/detail/CVE-2022-39254
- https://github.com/poljar/matrix-nio/commit/b1cbf234a831daa160673defd596e6450e9c29f0
- https://github.com/poljar/matrix-nio

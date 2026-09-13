# [H] Integer Underflow in Memory Range Check in Renesas RCAR

## Summary
Severity: High
Advisory: CVE-2024-6285
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-6285
Type: osv

## Details
Integer Underflow (Wrap or Wraparound) vulnerability in Renesas arm-trusted-firmware.
An integer underflow in image range check calculations could lead to bypassing address restrictions and loading of images to unallowed addresses.

## References
- https://asrg.io/security-advisories/cve-2024-6285/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6285.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6285
- https://github.com/renesas-rcar/arm-trusted-firmware/commit/b596f580637bae919b0ac3a5471422a1f756db3b
- https://github.com/renesas-rcar/arm-trusted-firmware

# [H] sharp inherited vulnerabilities in libvips: CVE-2026-33327, CVE-2026-33328, CVE-2026-35590, CVE-2026-35591

## Summary
Severity: High
Advisory: GHSA-f88m-g3jw-g9cj
CWE: CWE-1395
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-f88m-g3jw-g9cj
Type: github-advisory

## Affected
- npm: `sharp` — affected >=0 <0.35.0

## Details
### Impact

A number of vulnerabilities, two rated as "High" severity using CVSSv4, have been discovered and fixed in the upstream libvips dependency.

Those processing untrusted input with versions of sharp prior to 0.35.0 are affected.

### Patches

#### Using prebuilt binaries provided by sharp?

Most people rely on the prebuilt binaries provided by sharp.

Please upgrade sharp to the latest version, currently 0.35.3, which provides libvips 8.18.3.

#### Using a globally-installed libvips?

Please ensure you are using the latest libvips 8.18.3.

### Workarounds
Add the following to your code to prevent sharp from decoding GIF, TIFF and VIPS images.
```js
sharp.block({ operation: ["VipsForeignLoadNsgif", "VipsForeignLoadTiff", "VipsForeignLoadVips"] });
```

## References
- https://github.com/libvips/libvips/security/advisories/GHSA-2fcj-gj27-279x
- https://github.com/libvips/libvips/security/advisories/GHSA-523x-vhfw-6r76
- https://github.com/libvips/libvips/security/advisories/GHSA-jmwm-wc68-mhwm
- https://github.com/libvips/libvips/security/advisories/GHSA-r98w-4fp7-m9c7
- https://github.com/lovell/sharp/security/advisories/GHSA-f88m-g3jw-g9cj
- https://github.com/lovell/sharp

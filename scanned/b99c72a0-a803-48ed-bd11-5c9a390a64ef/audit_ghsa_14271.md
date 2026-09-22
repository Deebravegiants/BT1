# [M] Arbitrary File Read in Admin JS CSS files

## Summary
Severity: Medium
Advisory: GHSA-j5c3-r84f-9596
CVE: CVE-2023-30852
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-j5c3-r84f-9596
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact

It was observed that the `/admin/misc/script-proxy` API endpoint accessible by an authenticated administrator user and is vulnerable arbitrary JavaScript, CSS file read via the "scriptPath" and "scripts" parameters. The "scriptPath" parameter is not sanitized properly and is vulnerable to path traversal attack. Any JavaScript/CSS file from the application server can be read by specifying sufficient number of "../" patterns to go out from the application webroot followed by path of the folder where the file is located in the "scriptPath" parameter and the file name in the "scripts" parameter. The JavaScript file is successfully read only if the web application has read access to it.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/1d128404eddf4beb560d434437347da7aea059eb.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/1d128404eddf4beb560d434437347da7aea059eb.patch manually.

### References
https://github.com/pimcore/pimcore/pull/14959

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-j5c3-r84f-9596
- https://nvd.nist.gov/vuln/detail/CVE-2023-30852
- https://github.com/pimcore/pimcore/pull/14959
- https://github.com/pimcore/pimcore/commit/498cadec2292f7842fb10612068ac78496e884b4.patch
- https://github.com/pimcore/pimcore

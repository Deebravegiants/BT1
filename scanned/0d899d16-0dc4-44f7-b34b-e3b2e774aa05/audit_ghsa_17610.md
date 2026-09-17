# [M] Nautobot may allows uploaded media files to be accessible without authentication

## Summary
Severity: Medium
Advisory: GHSA-rh67-4c8j-hjjh
CVE: CVE-2025-49143
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-rh67-4c8j-hjjh
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=0 <1.6.32
- PyPI: `nautobot` — affected >=2.0.0 <2.4.10

## Details
### Impact

Files uploaded by users to Nautobot's `MEDIA_ROOT` directory, including DeviceType image attachments as well as images attached to a Location, Device, or Rack, are served to users via a URL endpoint that was not enforcing user authentication. As a consequence, such files can be retrieved by anonymous users who know or can guess the correct URL for a given file.

For DeviceType image attachments, a mitigating factor is that no URL endpoint exists for listing the contents of the `devicetype-images/` subdirectory, and the file names are as specified by the uploading user, so any given DeviceType image attachment can only be retrieved by correctly guessing its file name.

Similarly, for all other image attachments, while the images *can* be listed by accessing the `/api/extras/image-attachments/` endpoint *as an authenticated user only*, absent that authenticated access, accessing the files would again require guessing file names correctly.

### Patches

Nautobot v2.4.10 and v1.6.32 will address this issue by adding enforcement of Nautobot user authentication to this endpoint.

### Workarounds

No workaround other than applying the patch given in https://github.com/nautobot/nautobot/pull/6672 (2.x) or https://github.com/nautobot/nautobot/pull/6703 (1.6)

### References
_Are there any links users can visit to find out more?_

- https://github.com/nautobot/nautobot/commit/9c892dc300429948a4714f743c9c2879d8987340
- https://github.com/nautobot/nautobot/commit/d99a53b065129cff3a0fa9abe7355a9ef1ad4c95

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-rh67-4c8j-hjjh
- https://nvd.nist.gov/vuln/detail/CVE-2025-49143
- https://github.com/nautobot/nautobot/pull/6672
- https://github.com/nautobot/nautobot/pull/6703
- https://github.com/nautobot/nautobot/commit/9c892dc300429948a4714f743c9c2879d8987340
- https://github.com/nautobot/nautobot/commit/d99a53b065129cff3a0fa9abe7355a9ef1ad4c95
- https://github.com/nautobot/nautobot

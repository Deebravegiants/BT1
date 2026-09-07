# [M] pocketmine/raklib reliable-ordered queue size is unlimited, allowing a session to hog server memory

## Summary
Severity: Medium
Advisory: GHSA-w98g-5fmx-wm4x
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-w98g-5fmx-wm4x
Type: github-advisory

## Affected
- Packagist: `pocketmine/raklib` — affected >=0.14.0 <0.14.6
- Packagist: `pocketmine/raklib` — affected >=0.15.0 <0.15.1

## Details
### Impact
A client can send reliable-ordered packets 0, 2, 3, 4, 5 ... etc, and all the packets 2 and up will stay in the reliable-ordered queue until 1 arrives. A malicious client can exploit this to waste all available server memory by simply never sending the missing packet. Since the server doesn't make any effort to limit the size of the queue or detect this kind of abuse, this problem is easy to abuse.

### Patches
This bug was fixed on the 0.14.x and 0.15.x release lines by 371190f5854372154d1b263cd2a10e658e92bebe.

### Workarounds
No workaround is known.

## References
- https://github.com/pmmp/RakLib/security/advisories/GHSA-w98g-5fmx-wm4x
- https://github.com/pmmp/RakLib/commit/371190f5854372154d1b263cd2a10e658e92bebe
- https://github.com/pmmp/RakLib

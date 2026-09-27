# [H] Path Traversal: 'dir/../../filename' in moment.locale

## Summary
Severity: High
Advisory: GHSA-8hfj-j24r-96c4
CVE: CVE-2022-24785
CWE: CWE-22, CWE-27
Ecosystem: NuGet, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-04
Source: https://github.com/advisories/GHSA-8hfj-j24r-96c4
Type: github-advisory

## Affected
- npm: `moment` — affected >=0 <2.29.2
- NuGet: `Moment.js` — affected >=0 <2.29.2

## Details
### Impact
This vulnerability impacts npm (server) users of moment.js, especially if user provided locale string, eg `fr` is directly used to switch moment locale.

### Patches
This problem is patched in 2.29.2, and the patch can be applied to all affected versions (from 1.0.1 up until 2.29.1, inclusive).

### Workarounds
Sanitize user-provided locale name before passing it to moment.js.

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [moment repo](https://github.com/moment/moment)

## References
- https://github.com/moment/moment/security/advisories/GHSA-8hfj-j24r-96c4
- https://nvd.nist.gov/vuln/detail/CVE-2022-24785
- https://github.com/moment/moment/commit/4211bfc8f15746be4019bba557e29a7ba83d54c5
- https://github.com/moment/moment
- https://lists.debian.org/debian-lts-announce/2023/01/msg00035.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6QIO6YNLTK2T7SPKDS4JEL45FANLNC2Q
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ORJX2LF6KMPIHP6B2P6KZIVKMLE3LVJ5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6QIO6YNLTK2T7SPKDS4JEL45FANLNC2Q
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ORJX2LF6KMPIHP6B2P6KZIVKMLE3LVJ5
- https://security.netapp.com/advisory/ntap-20220513-0006
- https://security.netapp.com/advisory/ntap-20241108-0002
- https://www.tenable.com/security/tns-2022-09

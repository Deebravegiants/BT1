# [M] Pleezer resource exhaustion through uncollected hook script processes

## Summary
Severity: Medium
Advisory: GHSA-472w-7w45-g3w5
CVE: CVE-2025-32439
CWE: CWE-460, CWE-772
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-472w-7w45-g3w5
Type: github-advisory

## Affected
- crates.io: `pleezer` — affected >=0 <0.16.0

## Details
### Impact
Hook scripts in pleezer can be triggered by various events like track changes and playback state changes. In affected versions, these scripts were spawned without proper process cleanup, leaving zombie processes in the system's process table.

Even during normal usage, every track change and playback event would leave behind zombie processes. This leads to inevitable resource exhaustion over time as the system's process table fills up, eventually preventing new processes from being created. The issue is exacerbated if events occur rapidly, whether through normal use (e.g., skipping through a playlist) or potential manipulation of the Deezer Connect protocol traffic.

This vulnerability affects all users who have configured hook scripts using the `--hook` option.

### Patches
This issue has been fixed in version 0.16.0. Users should upgrade to this version, which properly manages child processes using asynchronous process handling and cleanup.

### Workarounds
Users who cannot upgrade immediately can:
- Disable hook scripts by removing the `--hook` option
- Ensure hook scripts handle their own child process cleanup
- Regularly restart pleezer to clear accumulated zombie processes

### References
- Initial report: https://github.com/roderickvd/pleezer/discussions/83#discussioncomment-12818199
- Fix commit: 436a5f1e4c08989b58dbba2b0ffa423458016c2d
- Fixed release: https://github.com/roderickvd/pleezer/releases/tag/v0.16.0

## References
- https://github.com/roderickvd/pleezer/security/advisories/GHSA-472w-7w45-g3w5
- https://nvd.nist.gov/vuln/detail/CVE-2025-32439
- https://github.com/roderickvd/pleezer/commit/436a5f1e4c08989b58dbba2b0ffa423458016c2d
- https://github.com/roderickvd/pleezer
- https://github.com/roderickvd/pleezer/discussions/83#discussioncomment-12818199
- https://github.com/roderickvd/pleezer/releases/tag/v0.16.0

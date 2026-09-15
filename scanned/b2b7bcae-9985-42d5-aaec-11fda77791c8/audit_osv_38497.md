# [M] libgphoto2 has OOB read in ptp_unpack_EOS_ImageFormat() and ptp_unpack_EOS_CustomFuncEx() due to missing length parameter in ptp-pack.c

## Summary
Severity: Medium
Advisory: CVE-2026-40333
Aliases: GHSA-hq94-cp6h-3gjp
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40333
Type: osv

## Details
libgphoto2 is a camera access and control library. In versions up to and including 2.5.33, two functions in camlibs/ptp2/ptp-pack.c accept a data pointer but no length parameter, performing unbounded reads. Their callers in ptp_unpack_EOS_events() have xsize available but never pass it, leaving both functions unable to validate reads against the actual buffer boundary. Commit 1817ecead20c2aafa7549dac9619fe38f47b2f53 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40333.json
- https://github.com/gphoto/libgphoto2/security/advisories/GHSA-hq94-cp6h-3gjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40333
- https://github.com/gphoto/libgphoto2/commit/1817ecead20c2aafa7549dac9619fe38f47b2f53

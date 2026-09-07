# [H] Viewing wget extractor output while logged in as an admin allows archived JS to execute in the admins context

## Summary
Severity: High
Advisory: GHSA-cr45-98w9-gwqx
CVE: CVE-2023-45815
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-cr45-98w9-gwqx
Type: github-advisory

## Affected
- PyPI: `archivebox` — affected >=0 <0.9.0

## Details
Related issue & discussion:

- https://github.com/ArchiveBox/ArchiveBox/issues/239
- https://github.com/ArchiveBox/ArchiveBox/wiki/Security-Overview#publishing
- https://github.com/ArchiveBox/ArchiveBox/wiki/Publishing-Your-Archive#security-concerns

### Impact

Any users who save untrusted URLs and view the content they output.

The impact is potentially severe if you are logged in to the ArchiveBox admin site in the same browser session and view an archived malicious page designed to target your ArchiveBox instance. Malicious JS could potentially act using your logged-in admin credentials and add/remove/modify snapshots, add/remove/modify ArchiveBox users, and generally do anything an admin user could do. 

The impact is less severe for non-logged-in users, as malicious JS cannot *modify* any archives, but it can still *read* all the other archived content by fetching the snapshot index and iterating through it.

Because all of ArchiveBox's archived content is served from the same host and port as the admin panel with 0 XSS protections, when archived pages are viewed the JS executes in the same context as all the other archived pages (and the admin panel), defeating most of the browser's usual CORS/CSRF security protections and leading to this issue.

### Patches

Follow here for progress on mitigating this issue: https://github.com/ArchiveBox/ArchiveBox/issues/239

### Workarounds

Disable the risky extractors by setting [`archivebox config --set SAVE_WGET=False SAVE_DOM=False`](https://github.com/ArchiveBox/ArchiveBox/wiki/Configuration#save_wget), ensure you are always logged out, or serve only a [static HTML version](https://github.com/ArchiveBox/ArchiveBox/wiki/Publishing-Your-Archive#2-export-and-host-it-as-static-html) of your archive.

### References

- https://en.wikipedia.org/wiki/Cross-site_request_forgery
- https://github.com/ArchiveBox/ArchiveBox#caveats
- https://github.com/ArchiveBox/ArchiveBox/wiki/Security-Overview
- https://github.com/ArchiveBox/ArchiveBox/wiki/Publishing-Your-Archive#security-concerns

## References
- https://github.com/ArchiveBox/ArchiveBox/security/advisories/GHSA-cr45-98w9-gwqx
- https://nvd.nist.gov/vuln/detail/CVE-2023-45815
- https://github.com/ArchiveBox/ArchiveBox/issues/239
- https://github.com/ArchiveBox/ArchiveBox/pull/1773
- https://github.com/ArchiveBox/ArchiveBox/commit/a6548df8d0aae1d3d326deb1191b128232708166
- https://en.wikipedia.org/wiki/Cross-site_request_forgery
- https://github.com/ArchiveBox/ArchiveBox
- https://github.com/ArchiveBox/ArchiveBox#caveats
- https://github.com/ArchiveBox/ArchiveBox/wiki/Configuration#save_wget
- https://github.com/ArchiveBox/ArchiveBox/wiki/Publishing-Your-Archive#2-export-and-host-it-as-static-html
- https://github.com/ArchiveBox/ArchiveBox/wiki/Publishing-Your-Archive#security-concerns
- https://github.com/ArchiveBox/ArchiveBox/wiki/Security-Overview
- https://github.com/pypa/advisory-database/tree/main/vulns/archivebox/PYSEC-2023-229.yaml

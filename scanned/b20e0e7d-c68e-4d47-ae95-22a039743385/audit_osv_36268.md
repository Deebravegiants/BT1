# [H] DevToys Path Traversal (“Zip Slip”) Vulnerability in DevToys Extension Installation

## Summary
Severity: High
Advisory: CVE-2026-22685
Aliases: GHSA-ggxr-h6fm-p2qh
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22685
Type: osv

## Details
DevToys is a desktop app for developers. In versions from 2.0.0.0 to before 2.0.9.0, a path traversal vulnerability exists in the DevToys extension installation mechanism. When processing extension packages (NUPKG archives), DevToys does not sufficiently validate file paths contained within the archive. A malicious extension package could include crafted file entries such as ../../…/target-file, causing the extraction process to write files outside the intended extensions directory. This flaw enables an attacker to overwrite arbitrary files on the user’s system with the privileges of the DevToys process. Depending on the environment, this may lead to code execution, configuration tampering, or corruption of application or system files. This issue has been patched in version 2.0.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22685.json
- https://github.com/DevToys-app/DevToys/security/advisories/GHSA-ggxr-h6fm-p2qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-22685
- https://github.com/DevToys-app/DevToys/commit/02fb7d46d9c663a4ee6ed968baa6a8810405047f
- https://github.com/DevToys-app/DevToys/pull/1643

# [H] CVE-2025-26794

## Summary
Severity: High
Advisory: CVE-2025-26794
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-21
Source: https://osv.dev/vulnerability/CVE-2025-26794
Type: osv

## Details
Exim 4.98 before 4.98.1, when SQLite hints and ETRN serialization are used, allows remote SQL injection. (Resolving SQL injection requires an update to 4.99.1 in certain non-default rate-limit configurations.)

## References
- http://www.openwall.com/lists/oss-security/2025/02/19/1
- http://www.openwall.com/lists/oss-security/2025/02/21/4
- http://www.openwall.com/lists/oss-security/2025/02/21/5
- https://code.exim.org/exim/exim/commit/bfe32b5c6ea033736a26da8421513206db9fe305
- https://exim.org
- https://exim.org/static/doc/security/EXIM-Security-2025-12-09.1/report.txt
- https://github.com/Exim/exim/wiki/EximSecurity
- https://www.exim.org/static/doc/security/CVE-2025-26794.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26794.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26794
- https://bugzilla.suse.com/show_bug.cgi?id=1237424
- https://github.com/NixOS/nixpkgs/pull/383926
- https://github.com/openbsd/ports/commit/584d2c49addce9ca0ae67882cc16969104d7f82d

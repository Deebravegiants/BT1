# [M] Arbitrary language parameter can passed to `aspell` executable via spelling requests in overleaf

## Summary
Severity: Medium
Advisory: CVE-2024-45312
Aliases: GHSA-pxm4-p454-vppg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-09-02
Source: https://osv.dev/vulnerability/CVE-2024-45312
Type: osv

## Details
Overleaf is a web-based collaborative LaTeX editor. Overleaf Community Edition and Server Pro prior to version 5.0.7 (or 4.2.7 for the 4.x series) contain a vulnerability that allows an arbitrary language parameter in client spelling requests to be passed to the `aspell` executable running on the server.  This causes `aspell` to attempt to load  a dictionary file with an arbitrary filename. File access is limited to the scope of the overleaf server. The problem is patched in versions 5.0.7 and 4.2.7.  Previous versions can be upgraded using the Overleaf toolkit `bin/upgrade` command. Users unable to upgrade may block POST requests to `/spelling/check` via a Web Application Firewall will prevent access to the vulnerable spell check feature.  However, upgrading is advised.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45312.json
- https://github.com/overleaf/overleaf/security/advisories/GHSA-pxm4-p454-vppg
- https://nvd.nist.gov/vuln/detail/CVE-2024-45312
- https://github.com/overleaf/overleaf/commit/b5e5d39c3ad4e7763d42b837738955f8ded4dcd3
- https://github.com/overleaf/toolkit

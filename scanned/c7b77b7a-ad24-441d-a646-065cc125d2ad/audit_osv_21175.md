# [M] CVE-2021-41089

## Summary
Severity: Medium
Advisory: CVE-2021-41089
Aliases: GHSA-v994-f8vw-g7j4, GO-2024-2913
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/CVE-2021-41089
Type: osv

## Details
Moby is an open-source project created by Docker to enable software containerization. A bug was found in Moby (Docker Engine) where attempting to copy files using `docker cp` into a specially-crafted container can result in Unix file permission changes for existing files in the host’s filesystem, widening access to others. This bug does not directly allow files to be read, modified, or executed without an additional cooperating process. This bug has been fixed in Moby (Docker Engine) 20.10.9. Users should update to this version as soon as possible. Running containers do not need to be restarted.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-222547.pdf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B5Q6G6I4W5COQE25QMC7FJY3I3PAYFBB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZNFADTCHHYWVM6W4NJ6CB4FNFM2VMBIB/
- https://github.com/moby/moby/security/advisories/GHSA-v994-f8vw-g7j4
- https://github.com/moby/moby/commit/bce32e5c93be4caf1a592582155b9cb837fc129a

# [H] OpenProject has SSRF and CSWSH in Hocuspocus Synchronization Server

## Summary
Severity: High
Advisory: CVE-2026-24772
Aliases: GHSA-r854-p5qj-x974
CVSS: 8.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24772
Type: osv

## Details
OpenProject is an open-source, web-based project management software. To enable the real time collaboration on documents, OpenProject 17.0 introduced a synchronization server. The OpenPrioject backend generates an authentication token that is currently valid for 24 hours, encrypts it with a shared secret only known to the synchronization server. The frontend hands this encrypted token and the backend URL over to the synchronization server to check user's ability to work on the document and perform intermittent saves while editing. The synchronization server does not properly validate the backend URL and sends a request with the decrypted authentication token to the endpoint that was given to the server. An attacker could use this vulnerability to decrypt a token that he intercepted by other means to gain an access token to interact with OpenProject on the victim's behalf. This vulnerability was introduced with OpenProject 17.0.0 and was fixed in 17.0.2. As a workaround, disable the collaboration feature via Settings -> Documents -> Real time collaboration -> Disable. Additionally the `hocuspocus` container should also be disabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24772.json
- https://github.com/opf/openproject/security/advisories/GHSA-r854-p5qj-x974
- https://nvd.nist.gov/vuln/detail/CVE-2026-24772

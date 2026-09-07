# [H] WsgiDAV encoded dot segments can escape filesystem share roots

## Summary
Severity: High
Advisory: GHSA-wxq4-cc2q-338q
CVE: CVE-2026-48099
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-wxq4-cc2q-338q
Type: github-advisory

## Affected
- PyPI: `wsgidav` — affected >=0 <4.3.4

## Details
### Impact
WsgiDAV 4.3.3 can allow a WebDAV request path containing an encoded parent-directory segment to escape the configured filesystem share root in a specific path layout.

### Patches
The issue is fixed with version 4.3.4.

### Preconditions

The practical impact depends on the deployment.

The deployment uses a filesystem-backed WsgiDAV share.

The attacker can send WebDAV requests accepted by that share. This may be an anonymous share or an authenticated WebDAV user. This is not an authentication bypass.

### Details

The issue is in `FilesystemProvider._loc_to_file_path()`. The method builds a candidate path with `os.path.abspath(os.path.join(root_path, *path_parts))`, then checks containment with `file_path.startswith(root_path)`. This is not path-boundary aware. For example, if the configured share root is `/tmp/share`, a resolved sibling path such as `/tmp/share_evil/secret.txt` still starts with the string `/tmp/share`.

In a local proof, this allowed GET, PUT, and DELETE requests to operate on files outside the configured share root.

The WSGI/server layer forwards the encoded dot segment to WsgiDAV's PATH_INFO. The local proof used `/%2e%2e/...`, which wsgiref passed through as `/../...`.

A sibling or neighboring path exists whose absolute path starts with the configured root path string, such as `/tmp/share` and `/tmp/share_evil`.

The WsgiDAV process has OS permissions for the outside path.

## References
- https://github.com/mar10/wsgidav/security/advisories/GHSA-wxq4-cc2q-338q
- https://github.com/mar10/wsgidav/commit/f894ed8656d7bdd7438ab8148c5a02546cb15183
- https://github.com/mar10/wsgidav

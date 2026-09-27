# [M] Smarty: Symlink path traversal out of trusted directories

## Summary
Severity: Medium
Advisory: GHSA-f6wf-28g6-769x
CVE: CVE-2026-62992
CWE: CWE-22, CWE-61
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-f6wf-28g6-769x
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=5.0.0 <5.8.2
- Packagist: `smarty/smarty` — affected >=0 <4.5.7

## Details
When Smarty's Security policy is enabled, secure_dir (and the configured template/trusted directories) restrict which local files a template may read via {include} and {fetch}. The trust check in Security::_checkDir() resolved the requested path with Smarty::_realpath(), which normalizes the path as a string only and does not follow symbolic links. A symlink placed inside a trusted directory therefore passed the trust check, while the underlying file_get_contents() followed it to an arbitrary file outside the sandbox (e.g. /etc/passwd).

## Impact
An attacker able to (a) cause a symlink to exist inside a trusted directory (e.g. a user-upload area located within the template path) and (b) cause a template to reference that path can read arbitrary files readable by the PHP process, escaping the secure_dir boundary. Confidentiality impact only.

## Patches
Fixed in 5.8.2. Security::_checkDir() now resolves the requested file with native realpath() and re-validates the canonical, symlink-free path against the trusted directories (which are canonicalized the same way, so legitimate symlinked deployment paths such as a Capistrano current symlink or macOS /var → /private/var keep working). It falls back to string normalization only when the file does not yet exist on disk.

## Workarounds
Ensure no untrusted symlinks can be created within any directory listed in secure_dir/the trusted template directories; restrict write access to those directories to trusted processes only.

## References
- Fix commit: 99c048c
- CWE-22

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-f6wf-28g6-769x
- https://github.com/smarty-php/smarty/commit/99c048ce7a590c519b79fbd38ad0143a08183a1f
- https://github.com/smarty-php/smarty/commit/a1ccdb0518021a559b4066c37b76a42c86bbce90
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v4.5.7
- https://github.com/smarty-php/smarty/releases/tag/v5.8.2

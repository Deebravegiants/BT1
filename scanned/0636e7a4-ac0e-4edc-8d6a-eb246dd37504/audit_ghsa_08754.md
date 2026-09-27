# [M] AsyncSSH `AuthorizedKeysFile %u` path traversal allows attacker-selected authorized keys to authenticate a traversal username

## Summary
Severity: Medium
Advisory: GHSA-g794-3fmp-753h
CVE: CVE-2026-45309
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-g794-3fmp-753h
Type: github-advisory

## Affected
- PyPI: `asyncssh` — affected >=2.22.0 <2.23.0

## Details
## Summary
AsyncSSH 2.22.0 expands the OpenSSH-compatible `AuthorizedKeysFile` `%u` token with the raw SSH username during pre-authentication server config reload. A server configured with a documented per-user key pattern such as `AuthorizedKeysFile authorized_keys/%u` can be made to read an authorized-keys file outside the intended directory when the SSH username contains path traversal segments. If the attacker can place or reference a readable authorized-keys-format file containing their public key, the attacker can authenticate over SSH as the traversal username.

## Affected Product
- Package: asyncssh
- Ecosystem: pip
- Affected versions: confirmed on 2.22.0; exact lower bound not finalized
- Tested version: 2.22.0
- Audit commit/tag: tag `v2.22.0`, commit `af5a81e669633d83d535163f93b6bf3f957c9238`
- PyPI sdist SHA256: `c3ce72b01be4f97b40e62844dd384227e5ff5a401a3793007c42f86a5c8eb537`

## Vulnerability Details
- CWE: CWE-22: Improper Limitation of a Pathname to a Restricted Directory
- Component: AsyncSSH server config reload and public-key authentication (`asyncssh/config.py`, `asyncssh/connection.py`, `asyncssh/auth_keys.py`, `asyncssh/misc.py`)
- Root cause: `%u` in `AuthorizedKeysFile` is expanded from the remote username without rejecting path separators or `..` segments, and the resulting path is opened without constraining it to the intended authorized-keys directory.
- Security boundary violated: the configured authorized-keys directory and public-key authentication trust boundary.
- Direct impact: public-key authentication succeeds using an attacker-selected authorized-keys file outside the intended directory.
- Chain impact, if any: none claimed; direct authentication impact is primary.

## Attack Preconditions
- The AsyncSSH server uses a config or equivalent pattern where `AuthorizedKeysFile` contains `%u`, for example `AuthorizedKeysFile authorized_keys/%u`.
- Public-key authentication is enabled.
- The attacker can place or reference a readable authorized-keys-format file outside the intended directory, such as a file in a world-writable or application-writable location.
- The application does not separately reject usernames containing `/`, `\`, or `..` before AsyncSSH uses the username for key-file selection.

## Reproduction
The run-scoped evidence contains a safe localhost proof:

1. Start the proof harness saved at 
[harness_app.py](https://github.com/user-attachments/files/27232526/harness_app.py)

2. Run 
[exploit_proof.py](https://github.com/user-attachments/files/27232538/exploit_proof.py)
through 
[run_proof.sh](https://github.com/user-attachments/files/27232545/run_proof.sh)

3. The harness creates `sshd_config` with `AuthorizedKeysFile authorized_keys/%u`, writes the attacker's public key to a file outside `authorized_keys/`, starts a real AsyncSSH server, and attempts two SSH logins.
4. Expected result: the normal username `victim` fails, while the traversal username authenticates with the same attacker key.

Observed proof output:

```text
[CONTROL] username=victim success=False
[ATTACK] username=../../../asyncssh-proof-exploit-proof-8b2bd23daeeb.pub success=True
[ATTACK] output=AUTH_BYPASS_SUCCESS username=../../../asyncssh-proof-exploit-proof-8b2bd23daeeb.pub
PASS: traversal username authenticated with attacker-controlled authorized_keys file
```

## References
- https://github.com/ronf/asyncssh/security/advisories/GHSA-g794-3fmp-753h
- https://github.com/ronf/asyncssh

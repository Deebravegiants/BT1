# [C] fast-mcp-telegram: Bearer token path traversal bypasses reserved Telegram session protection

## Summary
Severity: Critical
Advisory: GHSA-rxw2-pc8j-vxwm
CVE: CVE-2026-52830
CWE: CWE-22, CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-rxw2-pc8j-vxwm
Type: github-advisory

## Affected
- PyPI: `fast-mcp-telegram` — affected >=0 <0.19.1

## Details
## Summary

fast-mcp-telegram validates HTTP Bearer tokens by joining the raw token string into a session-file path. The verifier rejects the exact reserved token `telegram`, but it does not reject path separators or normalize the path before checking whether the session file exists. A remote HTTP client can therefore authenticate as the default legacy session with a token such as `../fast-mcp-telegram/telegram` when the documented default session file `~/.config/fast-mcp-telegram/telegram.session` exists.

This bypasses the reserved session name control that is intended to prevent HTTP multi-user sessions from colliding with the default stdio or legacy account. With account-prefixed MCP tools enabled, the attacker still sees and calls the prefixed tools for the default account, so the prefix middleware does not stop the session selection bypass.

## Impact

An unauthenticated network client can access the Telegram account represented by the default `telegram.session` file without knowing a generated bearer token, if that legacy or default session file is present on a server running HTTP auth. The attacker can then call Telegram MCP tools as that account, including message reading, message sending, MTProto API calls, and attachment-producing tool surfaces available to the session.

## Technical details

`SessionFileTokenVerifier.verify_token()` strips whitespace and rejects exact reserved names:

```python
if token.lower() in RESERVED_SESSION_NAMES:
    return None
```

It then appends `.session` to the raw token and checks the resulting path:

```python
session_path = self._session_directory / f"{token}.session"
if not session_path.is_file():
    return None
```

No check rejects `/`, `\\`, `..`, absolute paths, or resolved paths outside the configured session directory. The session client path is built the same way in `src/client/connection.py`:

```python
session_path = SESSION_DIR / f"{token}.session"
client = await _build_telegram_client_for_token(session_path, token)
```

With the default session directory, the token `../fast-mcp-telegram/telegram` resolves as follows:

```text
~/.config/fast-mcp-telegram/../fast-mcp-telegram/telegram.session
= ~/.config/fast-mcp-telegram/telegram.session
```

The exact token `telegram` is denied, but the traversal alias reaches the same file and is accepted. This is especially important because `telegram` is the documented default `session_name`, and the security documentation says reserved names are blocked to prevent conflicts with stdio and HTTP no-auth sessions.

The vulnerable code is present on current `master` commit `167ab705f1cd09b21e85c370570471fe75a4f8c9` and in release tag `0.19.0` commit `77bdf6d7e5c6a84d87acc423db613e6c6ba30094`.

## Reproduction

The following proof uses stub session files and stub Telegram clients, so it does not need real Telegram credentials. It validates the auth decision and the eventual session path used by the client builder.

Run on current master:

```bash
git clone https://github.com/leshchenko1979/fast-mcp-telegram.git
cd fast-mcp-telegram
python validation_token_traversal.py
```

The local proof script created for validation is attached below for reference:

```python
# High-level proof outline
# 1. Create a temporary session directory containing telegram.session and a random token session.
# 2. Instantiate SessionFileTokenVerifier with that directory.
# 3. Verify denied controls: token `telegram` is rejected, and a traversal token to a missing file is rejected.
# 4. Verify allowed control: a normal random token with a matching session file is accepted.
# 5. Verify bypass: token `../fast-mcp-telegram/telegram` is accepted and the client builder receives the default telegram.session path.
# 6. Verify prefix behavior: account-prefixed tools are listed for the traversal-authenticated default account, a prefixed call reaches send_message, and an unprefixed call is still denied.
```

Key controls from the current-master run:

```json
{
  "reserved_default_token_denied": true,
  "normal_random_token_allowed": true,
  "missing_traversal_token_denied": true,
  "traversal_alias_to_reserved_default_allowed": true,
  "traversal_access_token_value": "../fast-mcp-telegram/telegram",
  "client_builder_used_default_session_file": true,
  "prefixed_tool_listed_for_traversal_token": "defaultalice_send_message",
  "prefixed_tool_call_reached_handler_as": "send_message",
  "unprefixed_tool_call_denied_when_prefix_resolved": true
}
```

Interpretation:

1. Denied control: the exact reserved token `telegram` is rejected.
2. Allowed control: a normal random session token is accepted when its matching session file exists.
3. Denied control: a traversal token pointing to a missing file is rejected.
4. Bypass: `../fast-mcp-telegram/telegram` authenticates and the client builder receives the resolved default session path.
5. Prefix control: once authenticated through the traversal token, account-prefixed tools are listed and a prefixed `tools/call` reaches the internal `send_message` handler. An unprefixed call is rejected when the prefix resolves, so the confirmed bug is the session selection and authentication bypass, not a missing-prefix execution bypass.

## Why this crosses the auth boundary

A production HTTP auth deployment is expected to require high-entropy per-session bearer tokens. Reserved names are explicitly blocked because common names such as `telegram` can collide with the default session. The traversal alias turns the public token namespace back into a filesystem namespace and bypasses that reserved-name policy.

The account-prefix middleware is downstream of authentication. It labels tools based on the resolved Telegram account for the token that was accepted. Because the traversal token is accepted as a valid FastMCP `AccessToken`, the middleware correctly exposes the default account's prefixed tools to the attacker. It cannot recover the lost authentication boundary.

## Remediation

Reject bearer tokens that are not strict opaque token identifiers before using them in file paths. Recommended checks:

1. Accept only a safe token alphabet, for example `^[A-Za-z0-9_-]{32,128}$`, matching generated URL-safe base64 tokens.
2. Reject `/`, `\\`, `.`, `..`, empty segments, and absolute paths for both header auth and URL auth.
3. Resolve the final session path and require it to remain directly under the configured session directory:

```python
session_dir = self._session_directory.resolve()
session_path = (session_dir / f"{token}.session").resolve()
if session_path.parent != session_dir:
    return None
```

4. Apply the same validation in `SessionFileTokenVerifier`, URL auth middleware, setup flows, cleanup code, and any code that opens session files by token.
5. Add regression tests for exact reserved names, traversal aliases such as `../fast-mcp-telegram/telegram`, absolute paths, URL-encoded traversal if any route decodes path components, Windows separators, and normal generated tokens.

## References
- https://github.com/leshchenko1979/fast-mcp-telegram/security/advisories/GHSA-rxw2-pc8j-vxwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-52830
- https://github.com/alexeyleshchenko/fast-mcp-telegram
- https://github.com/pypa/advisory-database/tree/main/vulns/fast-mcp-telegram/PYSEC-2026-2473.yaml
- https://pypi.org/project/fast-mcp-telegram
- https://web.archive.org/web/20250926152207/https://github.com/leshchenko1979/fast-mcp-telegram

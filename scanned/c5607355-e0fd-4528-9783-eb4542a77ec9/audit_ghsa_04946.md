# [M] OpenBao: LDAPi ldaputil (wrong escape func)

## Summary
Severity: Medium
Advisory: GHSA-6mwx-4547-5vc9
CVE: CVE-2026-55770
CWE: CWE-90
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6mwx-4547-5vc9
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20260617104213-10b7825c714c

## Details
## 1. Description

### Component

`sdk/helper/ldaputil/client.go` — the shared LDAP utility library used by both the LDAP authentication backend and OpenLDAP secrets engine to construct LDAP search filters and bind DNs.

### Root Cause

The LDAP utility contains a **function selection error** that causes incorrect escaping of user-controlled input in LDAP filter construction. Two lines construct the `bindDN` using `EscapeLDAPValue()`:

```go
// Line 191 — UPN Domain path
bindDN = fmt.Sprintf("%s@%s", EscapeLDAPValue(username), cfg.UPNDomain)

// Line 193 — User DN path
bindDN = fmt.Sprintf("%s=%s,%s", cfg.UserAttr, EscapeLDAPValue(username), cfg.UserDN)
```

The problem: `EscapeLDAPValue()` implements **RFC 4514** escaping, which is designed for Distinguished Name (DN) components. It only escapes characters meaningful in DNs: `+`, `,`, `;`, `"`, `\`, `<`, `>`, and leading/trailing spaces.

LDAP **search filters** (RFC 4515) have a different set of special characters: `*`, `(`, `)`, `\`, and NUL (`\x00`). None of these are escaped by `EscapeLDAPValue()`. The correct function is `ldap.EscapeFilter()` from the `github.com/go-ldap/ldap/v3` package.

The irony: the same file uses `ldap.EscapeFilter()` correctly at lines 225-226 in `RenderUserSearchFilter()` for the `UserFilter` template path, but the `GetUserDN()` function at lines 191-193 uses the wrong escape function.

### Exploitation Mechanics

```
Username: alice)(objectClass=*
↓ EscapeLDAPValue (no-op — no DN special chars)
alice)(objectClass=*
↓ fmt.Sprintf("(&(objectClass=user)(sAMAccountName=%s))", escapedUsername)
(&(objectClass=user)(sAMAccountName=alice)(objectClass=*))
                              ^^ injection point
```

The filter `(&(objectClass=user)(sAMAccountName=alice)(objectClass=*))` is logically equivalent to:
- `sAMAccountName=alice` AND `objectClass=user` AND `objectClass=*`

Since all entries match `objectClass=*`, the filter matches **any user entry** where `sAMAccountName` is `alice`, effectively ignoring the `objectClass=user` constraint. By crafting more sophisticated injections (e.g., `alice)(|(sAMAccountName=admin`), the attacker can match arbitrary different user entries.

### Preconditions

- LDAP authentication backend must be configured
- Directory must be Active Directory (UPNDomain path) or use UserDN/UserAttr binding
- Attacker controls the `username` field at login time

## 2. Proof of Concept

```bash
# Login with LDAP injection payload as username
curl -k -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice)(sAMAccountName=*",
    "password": "anything"
  }' \
  https://localhost:8200/v1/auth/ldap/login/admin

# LDAP filter constructed:
# (&(objectClass=user)(sAMAccountName=alice)(sAMAccountName=*))
#                   injection ──────────^
# The filter matches the first user with objectClass=user
# If the LDAP server returns admin's entry first, the token
# is bound to the admin entity, inheriting all admin policies
```

The LDAP search returns whichever entry the server ranks highest among results. In Active Directory with default sorting, this is often the oldest or alphabetically first user — potentially an administrative account.

## 3. Impact

| Impact | Detail |
|--------|--------|
| **Confidentiality** | Token bound to a different LDAP user (e.g., admin) grants access to all secrets and policies belonging to that entity |
| **Integrity** | Ability to modify secrets, write policies, or configure backends as the impersonated user |
| **Availability** | Low direct impact, but administrative access enables disabling or misconfiguring the entire OpenBao instance |

**Likelihood: HIGH** — the escape function mismatch is a well-documented antipattern in OWASP LDAP Injection guidance. The attack is trivially exploitable with no special tooling beyond `curl`.

### Why This Is High Severity

The LDAP auth backend is frequently used as a **primary authentication method** for enterprise OpenBao deployments. A successful LDAP injection against this backend can bypass the entire authentication chain, granting administrative access to the secrets store without needing to compromise an actual admin account.

## 4. Remediation

### Primary Fix: Use ldap.EscapeFilter

Replace `EscapeLDAPValue` with `ldap.EscapeFilter` in both filter construction paths:

```go
import "github.com/go-ldap/ldap/v3"

// Line 191 — UPN Domain path
bindDN = fmt.Sprintf("%s@%s", ldap.EscapeFilter(username), cfg.UPNDomain)

// Line 193 — User DN path
bindDN = fmt.Sprintf("%s=%s,%s", cfg.UserAttr, ldap.EscapeFilter(username), cfg.UserDN)
```

`EscapeLDAPValue` is still the correct choice for actual DN construction (where values are used as RDN components rather than filter values), but any value interpolated into an LDAP filter string must use `ldap.EscapeFilter`.

### Audit: All Call Sites

Review all usages of `EscapeLDAPValue` across the codebase to ensure none are used in filter context:

```bash
grep -rn "EscapeLDAPValue" /root/cve-audit/openbao/
```

### Defense-in-Depth

- Apply the principle of least privilege to LDAP service accounts used by OpenBao
- Use `UserFilter` with explicit attribute constraints to limit the search scope

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-6mwx-4547-5vc9
- https://github.com/openbao/openbao/pull/3306
- https://github.com/openbao/openbao/commit/10b7825c714c1ef25b6c3c1c2cd6ecd8747c0659
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.5

# [H] Lemur: LDAP Filter Injection enables post-authentication privilege escalation

## Summary
Severity: High
Advisory: GHSA-3r34-vq8m-39gh
CVE: CVE-2026-44304
CWE: CWE-90
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-3r34-vq8m-39gh
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.0

## Details
## Description

### Overview

Lemur's LDAP authentication module (`lemur/auth/ldap.py`) constructs LDAP search filters using unsanitized user input via Python string interpolation. An authenticated LDAP user can inject LDAP filter metacharacters through the username field to manipulate group membership queries and escalate their privileges to administrator.

### Vulnerable Code

**Location:** `lemur/auth/ldap.py`, `_bind()` method

**Filter 1 — User lookup (line ~161):**
```python
ldap_filter = "userPrincipalName=%s" % self.ldap_principal
```

`self.ldap_principal` is derived directly from `args["username"]` submitted at `POST /auth/login` with no sanitization. The `ldap.filter.escape_filter_chars()` function is never called.

**Filter 2 — Active Directory group lookup (line ~189):**
```python
groupfilter = "(&(objectclass=group)(member:1.2.840.113556.1.4.1941:={}))".format(userdn)
```

The `userdn` value is derived from the LDAP response to the first unsanitized query, making it potentially tainted as well.

### Impact

An authenticated LDAP user can:

1. Inject LDAP filter syntax into the username field during login
2. Manipulate the group membership query to return arbitrary groups
3. Be assigned the `admin` role or any other privileged role in Lemur
4. Gain unauthorized access to all certificates, private keys (via `/certificates/<id>/key`), and CA configurations
5. Issue certificates under any authority

### Exploitation Constraint

The `simple_bind_s()` call must succeed before the injectable filter is reached, so the attacker requires valid LDAP credentials. This is a **post-authentication privilege escalation**.

### Steps to Reproduce

1. Deploy Lemur with LDAP authentication enabled:
   ```python
   LDAP_AUTH = True
   LDAP_IS_ACTIVE_DIRECTORY = True
   LDAP_BIND_URI = "ldaps://dc.corp.example.com"
   LDAP_BASE_DN = "DC=corp,DC=example,DC=com"
   LDAP_EMAIL_DOMAIN = "corp.example.com"
   ```
2. Create a valid LDAP user account
3. Send login request with crafted username containing LDAP metacharacters:
   ```
   POST /auth/login
   Content-Type: application/json

   {
     "username": "validuser)(memberOf=CN=LemurAdmins,DC=corp,DC=example,DC=com",
     "password": "validpassword"
   }
   ```
4. The LDAP filter becomes:
   ```
   userPrincipalName=validuser)(memberOf=CN=LemurAdmins,DC=corp,DC=example,DC=com@corp.example.com
   ```
5. Depending on the LDAP server's parsing, this can alter query semantics
6. The user is assigned roles they should not have access to

### Remediation

Apply `ldap.filter.escape_filter_chars()` to all user-controlled values before interpolation:

```python
from ldap.filter import escape_filter_chars

# Fix 1: User lookup filter
ldap_filter = "userPrincipalName=%s" % escape_filter_chars(self.ldap_principal)

# Fix 2: Active Directory group filter
groupfilter = "(&(objectclass=group)(member:1.2.840.113556.1.4.1941:={}))".format(
    escape_filter_chars(userdn)
)
```

### Resources

- CWE-90: https://cwe.mitre.org/data/definitions/90.html
- OWASP LDAP Injection: https://owasp.org/www-community/attacks/LDAP_Injection
- Python ldap.filter.escape_filter_chars: https://www.python-ldap.org/en/python-ldap-3.4.0/reference/ldap-filter.html

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-3r34-vq8m-39gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44304
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.0

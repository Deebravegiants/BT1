# [M] Yamcs Vulnerable to LDAP Injection in LdapAuthModule

## Summary
Severity: Medium
Advisory: GHSA-cqh3-jg8p-336j
CVE: CVE-2026-42568
CWE: CWE-90
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-cqh3-jg8p-336j
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.7

## Details
### Summary

An LDAP injection vulnerability exists in `org.yamcs.security.LdapAuthModule` when constructing search filters. The username parameter is inserted directly into the LDAP filter without proper RFC 4515 escaping.

### Root Cause

**File:** `yamcs-core/src/main/java/org/yamcs/security/LdapAuthModule.java:233`

The `username` parameter is inserted directly into an LDAP search filter without RFC 4515 escaping:

```java
// VULNERABLE
var filter = userFilter.replace("{0}", username);
var searchResult = getSingleResult(ctx, userBase, filter, controls);
```

LDAP wildcard characters (`*`, `(`, `)`) are accepted without sanitization.

### Impact

With a known valid password, `username=*` authenticates as the first user returned by the LDAP search — enabling horizontal privilege escalation between accounts sharing similar passwords or when the attacker knows one valid password.

This affects deployments that use `org.yamcs.security.LdapAuthModule` in their `etc/security.yaml` configuration file.

### Proof of Concept

```bash
curl -X POST "http://TARGET:8090/auth/token" \
  -d "grant_type=password&username=*&password=known_password"
# Returns token for first matching LDAP user
```

### Fix

Apply RFC 4515 escaping before filter construction:

```java
private static String escapeLdapFilter(String input) {
    return input
        .replace("\\", "\\5c")
        .replace("*",  "\\2a")
        .replace("(",  "\\28")
        .replace(")",  "\\29")
        .replace("\0", "\\00");
}
var filter = userFilter.replace("{0}", escapeLdapFilter(username));
```

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-cqh3-jg8p-336j
- https://nvd.nist.gov/vuln/detail/CVE-2026-42568
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.12.7
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.13.0

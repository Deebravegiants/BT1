# [M] Eclipse Jetty: Path parameter traversal

## Summary
Severity: Medium
Advisory: GHSA-w7x5-g22v-xqhr
CVE: CVE-2026-8384
CWE: CWE-647
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-w7x5-g22v-xqhr
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-util` — affected >=12.0.0 <12.0.35
- Maven: `org.eclipse.jetty:jetty-util` — affected >=12.1.0 <12.1.9

## Details
### Description (as reported)

#### Summary

In Jetty 12.1.8, org.eclipse.jetty.util.URIUtil.canonicalPath() may leave dot-dot path segments unnormalized when a semicolon path parameter marker is followed by a slash and a dot
  segment.

A minimal example is:

`/public;/../admin/secret`

In my local reproduction, URIUtil.canonicalPath() returns:

`/public/../admin/secret`

instead of the expected normalized path:

`/admin/secret`

When Jetty's `SecurityHandler.PathMapped` is used to protect a path prefix such as `/admin/*`, the non-normalized canonical path may not match the protected prefix. As a result, an unauthenticated request may bypass the configured path-based security constraint.



#### Tested Version

Jetty: 12.1.8
JDK: 17.0.18
Maven: 3.9.14

Maven artifacts used:

  org.eclipse.jetty:jetty-server:12.1.8
  org.eclipse.jetty:jetty-security:12.1.8
  org.eclipse.jetty:jetty-session:12.1.8

Only confirmed Jetty 12.1.8 so far. 


#### Minimal Reproduction

Starts a minimal Jetty server with the following security setup:

```java
SecurityHandler.PathMapped security = new SecurityHandler.PathMapped();
security.put("/admin/*", Constraint.from("admin"));
security.put("/*", Constraint.ALLOWED);
security.setAuthenticator(new BasicAuthenticator());
```

The test then sends requests with no `Authorization` header.

Observed result:

```
GET /admin/secret                  -> 401
GET /public;x/../admin/secret      -> 200
```

The handler receives paths such as:

`/public/../admin/secret`

This suggests that the `/admin/*` security constraint is bypassed because `PathMapped` matching is performed against the non-normalized canonical path.


#### Suspected Root Cause

The suspected root cause is in `URIUtil.canonicalPath()`.

The relevant logic is approximately:

```java
    for (int i = 0; i < end; i++)
    {
        char c = encodedPath.charAt(i);

        switch (c)
        {
            case ';':
                if (builder == null)
                {
                    builder = new Utf8StringBuilder(encodedPath.length());
                    builder.append(encodedPath, 0, i);
                }

                while (++i < end)
                {
                    if (encodedPath.charAt(i) == '/')
                    {
                        builder.append('/');
                        break;
                    }
                }
                break;

            case '.':
                if (slash)
                    normal = false;
                if (builder != null)
                    builder.append(c);
                break;
        }

        slash = c == '/';
    }

    String canonical = (builder != null)
        ? (onBadUtf8 == null ? builder.toCompleteString() : builder.takeCompleteString(onBadUtf8))
        : encodedPath;
    return normal ? canonical : normalizePath(canonical);
```

For the input:

`/public;/../admin/secret`

when the outer loop reaches the semicolon:

```
    i      = 7
    c      = ';'
    slash  = false
    normal = true
```

Inside `case ';'`, the `while (++i < end)` loop advances i to the next character, which is already '/' for the empty path parameter form ";/".

The code then appends '/' to the canonical builder:

`builder.append('/');`

At this point, the canonical builder ends with '/':

`/public/`

However, the local variable `c` is still the old value ';', because `c` was read before entering the switch and is not updated when the inner loop advances `i`.

After leaving the switch, the loop updates the slash state using:

`slash = c == '/';`

Since `c` is still ';', slash becomes `false`.

On the next iteration, the scanner reaches '.', which is the first dot in the following "../" segment. Because slash is incorrectly `false`, this code does not run:

```java
    if (slash)
        normal = false;
```

Therefore `normal` remains `true`, and `canonicalPath()` returns the canonical string directly instead of calling `normalizePath(canonical)`.

The result is:

`/public/../admin/secret`

instead of:

`/admin/secret`

In short:

`case ';'` advances the scan position i and appends '/' to the canonical builder, but the loop tail still updates slash from the stale character `c=';'`. As a result, the following dot-dot segment is not detected as a path traversal segment.

####  More Precise Trigger Condition

The issue is not limited to a non-empty path parameter such as ";x".

The more precise trigger shape is:

`;[^/]*/.`

Examples:

```
    /public;/../admin/secret
    /public;x/../admin/secret
    /public;anything/../admin/secret
    /public;/./admin/secret
```

The minimal form is:

`/public;/../admin/secret`

because the semicolon is immediately followed by '/', so the inner while loop reaches '/' on its first increment.

####  Potential Minimal Fix Direction

A minimal fix would be to ensure that, when case ';' consumes input until '/' and appends '/' to the canonical builder, the slash state reflects the last effective character in the canonical path.

For example, conceptually:

```java
    case ';':
        if (builder == null)
        {
            builder = new Utf8StringBuilder(encodedPath.length());
            builder.append(encodedPath, 0, i);
        }

        while (++i < end)
        {
            if (encodedPath.charAt(i) == '/')
            {
                builder.append('/');
                slash = true;
                break;
            }
        }
        continue;
```

The important part is to avoid the loop tail from overwriting slash using the stale `c` value:

`slash = c == '/';`

In other words, `slash` should represent the last effective character appended to the canonical builder, not the original input character read before case ';' advanced `i`.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-w7x5-g22v-xqhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-8384
- https://github.com/jetty/jetty.project/pull/14969
- https://github.com/jetty/jetty.project/pull/14973
- https://github.com/jetty/jetty.project/commit/82969c77f6da46e27008b10b3c14840cd31db084
- https://github.com/jetty/jetty.project/commit/ade27ce93a37c33278720250d85c48601230ae3f
- https://github.com/jetty/jetty.project
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.0.35
- https://github.com/jetty/jetty.project/releases/tag/jetty-12.1.9
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/108

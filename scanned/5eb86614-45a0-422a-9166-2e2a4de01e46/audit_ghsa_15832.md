# [H] OpenRefine's PreviewExpressionCommand, which is eval, lacks protection against cross-site request forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-3jm4-c6qf-jrh3
CVE: CVE-2024-47879
CWE: CWE-352, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-3jm4-c6qf-jrh3
Type: github-advisory

## Affected
- Maven: `org.openrefine:main` — affected >=0 <3.8.3

## Details
### Summary

Lack of CSRF protection on the `preview-expression` command means that visiting a malicious website could cause an attacker-controlled expression to be executed. The expression can contain arbitrary Clojure or Python code.

The attacker must know a valid project ID of a project that contains at least one row.

### Details

The `com.google.refine.commands.expr.PreviewExpressionCommand` class contains the following comment:
```
/**
 * The command uses POST but does not actually modify any state so it does not require CSRF.
 */
```

However, this appears to be false (or no longer true). The expression being previewed (executed) can be written in GREL, Python, or Clojure. Since there are no restrictions on what code can be executed, the expression can do anything the user running OpenRefine can do. For instance, the following expressions start a calculator:

```
clojure:(.exec (Runtime/getRuntime) "gnome-calculator")
```

```
jython:import os;os.system("gnome-calculator")
```

The lack of restrictions on expressions is arguably not a problem if the user is typing their own expressions into OpenRefine: they could have just as well typed them into Clojure or Python directly. However, since the `preview-expression` command does not check for a CSRF token, the expression can actually come from a HTML form submitted by a different origin, including arbitrary websites.

Issue #2164 suggested adding CSRF protection to all endpoints, but this endpoint was skipped (and the above comment added) in the associated PR #2182.

### PoC

An example "malicious" page is at https://wandernauta.nl/or/ (of course, actual malicious pages would not wait for the victim to press the submit button).

The following curl command (substituting the project ID) also demonstrates the issue:

```sh
curl -d project=123456789 -d cellIndex=1 -d rowIndices='[0]' -d 'expression=clojure:(.exec (Runtime/getRuntime) "gnome-calculator")' http://localhost:3333/command/core/preview-expression/
```

### Impact

CSRF into remote code execution, provided the attacker knows at least one project ID in the victim's workspace and can convince the victim to open a malicious webpage.

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-3jm4-c6qf-jrh3
- https://nvd.nist.gov/vuln/detail/CVE-2024-47879
- https://github.com/OpenRefine/OpenRefine/commit/090924ca923489b6c94397cf1f5df7f7f78f0126
- https://github.com/OpenRefine/OpenRefine

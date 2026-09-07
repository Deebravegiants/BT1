# [M] OpenRefine's error page lacks escaping, leading to potential Cross-site Scripting on import of malicious project

## Summary
Severity: Medium
Advisory: GHSA-j8hp-f2mj-586g
CVE: CVE-2024-47882
CWE: CWE-79, CWE-81
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-j8hp-f2mj-586g
Type: github-advisory

## Affected
- Maven: `org.openrefine:openrefine` — affected >=0 <3.8.3

## Details
### Summary

The built-in "Something went wrong!" error page includes the exception message and exception traceback without escaping HTML tags, enabling injection into the page if an attacker can reliably produce an error with an attacker-influenced message.

It appears that the only way to reach this code in OpenRefine itself is for an attacker to somehow convince a victim to import a malicious file, as in GHSA-m88m-crr9-jvqq, which may be difficult.  However, out-of-tree extensions may add their own calls to `respondWithErrorPage`.

### Details

The `Command.respondWithErrorPage` (through `HttpUtilities.respondWithErrorPage`) function renders the Velocity template `error.vt`, which contains the `$message` and `$stack` variables, which are included in the response as-is:

https://github.com/OpenRefine/OpenRefine/blob/master/main/webapp/modules/core/error.vt#L52-L53

However, the message can contain HTML tags, which would then be interpreted by the browser. A mitigation would be to escape both the message and stack trace, perhaps using Guava's HTML escaper.

Flows that report errors as `application/json` responses are not interpreted by the browser and so not affected by this issue.

### PoC

In OpenRefine, use the "Import project" feature to import the following URL (or upload it as a file): https://wandernauta.nl/oa/example.tar.gz

A JavaScript alert appears.

### Impact

Execution of arbitrary JavaScript in the victim's browser, provided the victim can be convinced to import a malicious project. The script can do anything the user can do.

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-j8hp-f2mj-586g
- https://nvd.nist.gov/vuln/detail/CVE-2024-47882
- https://github.com/OpenRefine/OpenRefine/commit/85594e75e7b36025f7b6a67dcd3ec253c5dff8c2
- https://github.com/OpenRefine/OpenRefine
- https://github.com/OpenRefine/OpenRefine/blob/master/main/webapp/modules/core/error.vt#L52-L53

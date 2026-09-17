# [H] CVE-2021-21363

## Summary
Severity: High
Advisory: CVE-2021-21363
Aliases: GHSA-pc22-3g76-gm6j
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2021-21363
Type: osv

## Details
swagger-codegen is an open-source project which contains a template-driven engine to generate documentation, API clients and server stubs in different languages by parsing your OpenAPI / Swagger definition. In swagger-codegen before version 2.4.19, on Unix like systems, the system's temporary directory is shared between all users on that system. A collocated user can observe the process of creating a temporary sub directory in the shared temporary directory and race to complete the creation of the temporary subdirectory. This vulnerability is local privilege escalation because the contents of the `outputFolder` can be appended to by an attacker. As such, code written to this directory, when executed can be attacker controlled. For more details refer to the referenced GitHub Security Advisory. This vulnerability is fixed in version 2.4.19. Note this is a distinct vulnerability from CVE-2021-21364.

## References
- https://github.com/swagger-api/swagger-codegen/commit/987ea7a30b463cc239580d6ad166c707ae942a89
- https://github.com/swagger-api/swagger-codegen/security/advisories/GHSA-pc22-3g76-gm6j

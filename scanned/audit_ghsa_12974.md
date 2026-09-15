# [M] Datasette 1.0 alpha series leaks names of databases and tables to unauthenticated users

## Summary
Severity: Medium
Advisory: GHSA-7ch3-7pp7-7cpq
CVE: CVE-2023-40570
CWE: CWE-200, CWE-213
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-22
Source: https://github.com/advisories/GHSA-7ch3-7pp7-7cpq
Type: github-advisory

## Affected
- PyPI: `datasette` — affected >=1.0a0 <1.0a4

## Details
### Impact

This bug affects Datasette instances running a Datasette 1.0 alpha - 1.0a0, 1.0a1, 1.0a2 or 1.0a3 - in an online accessible location but with authentication enabled using a plugin such as [datasette-auth-passwords](https://datasette.io/plugins/datasette-auth-passwords).

The `/-/api` API explorer endpoint could reveal the names of both databases and tables - but not their contents - to an unauthenticated user.

### Patches

Datasette 1.0a4 has a fix for this issue.

### Workarounds

To work around this issue, block all traffic to the `/-/api` endpoint. This can be done with a proxy such as Apache or NGINX, or by installing the [datasette-block](https://datasette.io/plugins/datasette-block) plugin and adding the following configuration to your `metadata.json` or `metadata.yml` file:

```json
{
    "plugins": {
        "datasette-block": {
            "prefixes": ["/-/api"]
        }
    }
}
```
This will block access to the API explorer but will still allow access to the Datasette read or write JSON APIs, as those use different URL patterns within the Datasette `/database` hierarchy.

## References
- https://github.com/simonw/datasette/security/advisories/GHSA-7ch3-7pp7-7cpq
- https://nvd.nist.gov/vuln/detail/CVE-2023-40570
- https://github.com/simonw/datasette/commit/01e0558825b8f7ec17d3b691aa072daf122fcc74
- https://github.com/pypa/advisory-database/tree/main/vulns/datasette/PYSEC-2023-154.yaml
- https://github.com/simonw/datasette

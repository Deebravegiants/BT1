# [H] Canonical LXD Arbitrary File Read via Template Injection in Snapshot Patterns

## Summary
Severity: High
Advisory: GHSA-w2hg-2v4p-vmh6
CVE: CVE-2025-54287
CWE: CWE-1336
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-w2hg-2v4p-vmh6
Type: github-advisory

## Affected
- Go: `github.com/lxc/lxd` — affected >=4.0.0 <5.21.4
- Go: `github.com/lxc/lxd` — affected >=6.0.0 <6.5.0
- Go: `github.com/lxc/lxd` — affected >=0.0.0-20200331193331-03aab09f5b5c <0.0.0-20250827065555-0494f5d47e41

## Details
### Impact
In LXD's instance snapshot creation functionality, the Pongo2 template engine is used in the `snapshots.pattern` configuration for generating snapshot names. While code execution functionality has not been found in this template engine, it has file reading capabilities, creating a vulnerability that allows arbitrary file reading through template injection attacks.

### Reproduction Steps

1. Log in to LXD-UI with an account that has permissions to modify instance settings
2. Set the following template injection payload in the instance snapshot pattern:

```
{% filter urlencode|slice:":100" %}{% include "/etc/passwd" %}{%endfilter %}
```

Note that the above template uses the Pongo2 template engine's include tag to read system files. It also uses urlencode and slice filters to bypass character count and type restrictions.

3. Set scheduled snapshots to run every minute and wait for snapshot generation
4. Wait about a minute and confirm that file contents can be obtained from the created snapshot name

### Risk
The attack requires having configuration change permissions for LXD instances.
The attack allows reading arbitrary files accessible with LXD process permissions. This could lead to leakage of the following information:
-​ LXD host configuration files (/etc/passwd, /etc/shadow, etc.)
-​ LXD database files (containing information about all projects and instances)
-​ Configuration files and data of other instances
-​ Sensitive information on the host system

### Countermeasures
Pongo2 provides mechanisms for sandboxing templates.

> Template sandboxing (directory patterns, banned tags/filters)
( https://github.com/flosch/pongo2/tree/master?tab=readme-ov-file#features )

This functionality allows banning specific tags and filters by generating a custom TemplateSet.

At minimum, the following tags are considered to pose a risk of file leakage on the LXD host when used. Therefore, banning these can provide countermeasures against file reading attacks.
-​ include
-​ ssi
-​ extends
-​ import

The deny-list approach is prone to vulnerability recurrence due to missed countermeasures or new feature additions. Therefore, as the safest approach, we recommend using an allow-list format to permit only necessary functions.

However, as far as our investigation shows, pongo2 does not have functionality to retrieve a list of registered tags or filters, nor does it provide means to implement an allow-list approach. Therefore, it is necessary to either forcibly obtain the registration list through reflection and ban anything not on the allow-list, or ban everything from the current implemented list since the library has not been updated for about two years.

In LXD's implementation, template injection attacks can be prevented by modifying the `RenderTemplate` function in `shared/util.go` to use a restricted `TemplateSet` as shown above.

### Patches

| LXD Series  | Status |
| ------------- | ------------- |
| 6 | Fixed in LXD 6.5  |
| 5.21 | Fixed in LXD 5.21.4  |
| 5.0 | Ignored - Not critical  |
| 4.0  | Ignored - EOL and not critical |

### References
Reported by GMO Flatt Security Inc.

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-w2hg-2v4p-vmh6
- https://nvd.nist.gov/vuln/detail/CVE-2025-54287
- https://github.com/canonical/lxd
- https://pkg.go.dev/vuln/GO-2025-4004

# [M] fish-shop/syntax-check Improper Neutralization of Delimiters

## Summary
Severity: Medium
Advisory: GHSA-xj87-mqvh-88w2
CVE: CVE-2024-42482
CWE: CWE-140
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-xj87-mqvh-88w2
Type: github-advisory

## Affected
- GitHub Actions: `fish-shop/syntax-check` — affected >=0 <1.6.12

## Details
### Impact

Improper neutralisation of delimiters in the `pattern` input (specifically the command separator `;` and command substitution characters `(` and `)`) mean that arbitrary command injection is possible by modification of the input value used in a workflow. This has the potential for exposure or exfiltration of sensitive information from the workflow runner, such as might be achieved by sending environment variables to an external entity.

### Patches

As of this writing, the issue has been patched for versions in the `v1.x.x` release series in release `v1.6.12` (also tagged as `v1.6` and `v1`). The latest available release `v2.0.0` also includes a corresponding patch (also tagged as `v2.0` and `v2`).

Users should upgrade to at least the patched version `v1.6.12` or preferably the latest available version `v2.0.0`. Workflows that use the action ref `v1` will automatically receive the patched version `v1.6.12` in future workflow runs.

Patch summary:

| Release series | Patched tags    | Patched commit hashes |
|----------------|-------------------------|-------------|
| `1.x.x`        | `v1.6.12`, `v1.6`, `v1` | `91e6817c48ad475542fe4e78139029b036a53b03`    |
| `2.x.x`        | `v2.0.0`, `v2.0`, `v2`  | `c2cb11395e21119ff8d6e7ea050430ee7d6f49ca`    |

### Workarounds

Is it recommended that users update to the patched version `v1.6.12` or the latest release version `v2.0.0`, however remediation may be possible through careful control of workflows and the `pattern` input value used by this action.

### References

- [CWE-140: Improper Neutralization of Delimiters](https://cwe.mitre.org/data/definitions/140.html)
- [CAPEC-15: Command Delimiters](https://capec.mitre.org/data/definitions/15.html)

## References
- https://github.com/fish-shop/syntax-check/security/advisories/GHSA-xj87-mqvh-88w2
- https://nvd.nist.gov/vuln/detail/CVE-2024-42482
- https://github.com/fish-shop/syntax-check/commit/91e6817c48ad475542fe4e78139029b036a53b03
- https://github.com/fish-shop/syntax-check/commit/c2cb11395e21119ff8d6e7ea050430ee7d6f49ca
- https://github.com/fish-shop/syntax-check

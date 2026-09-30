# [M] Workflow re-write vulnerability using input parameter

## Summary
Severity: Medium
Advisory: GHSA-h563-xh25-x54q
CVE: CVE-2021-37914
CWE: CWE-20
Ecosystem: Go
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-h563-xh25-x54q
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.1.0 <3.1.6

## Details
### Impact

* Allow end-users to set input parameters, but otherwise expect workflows to be secure.

### Patches

Not yet.

### Workarounds

* Set `EXPRESSION_TEMPLATES=false` for the workflow controller


### References

* https://github.com/argoproj/argo-workflows/issues/6441

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-h563-xh25-x54q
- https://nvd.nist.gov/vuln/detail/CVE-2021-37914
- https://github.com/argoproj/argo-workflows/issues/6441
- https://github.com/argoproj/argo-workflows/pull/6285
- https://github.com/argoproj/argo-workflows/pull/6442
- https://github.com/argoproj/argo-workflows/commit/2a2ecc916925642fd8cb1efd026588e6828f82e1
- github.com/argoproj/argo-workflows/v3

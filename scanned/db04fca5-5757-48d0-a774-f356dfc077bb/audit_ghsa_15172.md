# [M] `goreleaser release --debug` shows secrets

## Summary
Severity: Medium
Advisory: GHSA-h3q2-8whx-c29h
CVE: CVE-2024-23840
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-h3q2-8whx-c29h
Type: github-advisory

## Affected
- Go: `github.com/goreleaser/goreleaser` — affected >=1.23.0 <1.24.0

## Details
### Summary
Hello 👋 

`goreleaser release --debug` log shows secret values used in the in the custom publisher.


How to reproduce the issue:

- Define a custom publisher as the one below. Make sure to provide a custom script to the `cmd` field and to provide a secret to `env` 

```
#.goreleaser.yml 
publishers:
  - name: my-publisher
  # IDs of the artifacts we want to sign
    ids:
      - linux_archives
      - linux_package
    cmd: "./build/package/linux_notarize.sh"
    env:
      - VERSION={{ .Version }}
      - SECRET_1={{.Env.SECRET_1}}
      - SECRET_2={{.Env.SECRET_2}}
```

- run `goreleaser release --debug`

You should see your secret value in the gorelease log. The log shows also the `GITHUB_TOKEN`

Example:

```
running                                        cmd= ....
SECRET_1=secret_value
```

## References
- https://github.com/goreleaser/goreleaser/security/advisories/GHSA-h3q2-8whx-c29h
- https://nvd.nist.gov/vuln/detail/CVE-2024-23840
- https://github.com/goreleaser/goreleaser/commit/d5b6a533ca1dc3366983d5d31ee2d2b6232b83c0
- https://github.com/goreleaser/goreleaser

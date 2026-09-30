# [C] Pomerium vulnerable to Incorrect Authorization with specially crafted requests

## Summary
Severity: Critical
Advisory: GHSA-pvrc-wvj2-f59p
Aliases: CVE-2023-33189, GO-2023-1800
Ecosystem: Go
Published: 2023-05-26
Source: https://osv.dev/vulnerability/GHSA-pvrc-wvj2-f59p
Type: osv

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0.22.0 <0.22.2
- Go: `github.com/pomerium/pomerium` — affected >=0.21.0 <0.21.4
- Go: `github.com/pomerium/pomerium` — affected >=0.20.0 <0.20.1
- Go: `github.com/pomerium/pomerium` — affected >=0.19.0 <0.19.2
- Go: `github.com/pomerium/pomerium` — affected >=0.18.0 <0.18.1
- Go: `github.com/pomerium/pomerium` — affected >=0 <0.17.4

## Details
### Impact

With specially crafted requests, incorrect authorization decisions may be made by Pomerium.

### Patches

We are releasing patch fixes to address this vulnerability going back to `v0.17.X`. Please upgrade to:

- v0.22.2
- v0.21.4
- v0.20.1
- v0.19.2
- v0.18.1
- v0.17.4


### For more information

If you have any questions or comments about this advisory:

- Open an issue in [pomerium/pomerium](https://github.com/pomerium/pomerium/issues)
- Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-pvrc-wvj2-f59p
- https://nvd.nist.gov/vuln/detail/CVE-2023-33189
- https://github.com/pomerium/pomerium/commit/d315e683357a9b587ba9ef399a8813bcc52fdebb
- https://github.com/pomerium/pomerium
- https://github.com/pomerium/pomerium/releases/tag/v0.17.4
- https://github.com/pomerium/pomerium/releases/tag/v0.18.1
- https://github.com/pomerium/pomerium/releases/tag/v0.19.2
- https://github.com/pomerium/pomerium/releases/tag/v0.20.1
- https://github.com/pomerium/pomerium/releases/tag/v0.21.4
- https://github.com/pomerium/pomerium/releases/tag/v0.22.2

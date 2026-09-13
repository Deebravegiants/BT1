# [M] CVE-2019-15716

## Summary
Severity: Medium
Advisory: CVE-2019-15716
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-28
Source: https://osv.dev/vulnerability/CVE-2019-15716
Type: osv

## Details
WTF before 0.19.0 does not set the permissions of config.yml, which might make it easier for local attackers to read passwords or API keys if the permissions were misconfigured or were based on unsafe OS defaults.

## References
- https://github.com/wtfutil/wtf/issues/517
- https://github.com/wtfutil/wtf/compare/v0.18.0...v0.19.0
- https://github.com/wtfutil/wtf/blob/67658e172c9470e93e4122d6e2c90d01db12b0ac/cfg/config_files.go#L71-L72

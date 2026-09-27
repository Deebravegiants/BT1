# [M] CVE-2020-12872

## Summary
Severity: Medium
Advisory: CVE-2020-12872
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-15
Source: https://osv.dev/vulnerability/CVE-2020-12872
Type: osv

## Details
yaws_config.erl in Yaws through 2.0.2 and/or 2.0.7 loads obsolete TLS ciphers, as demonstrated by ones that allow Sweet32 attacks, if running on an Erlang/OTP virtual machine with a version less than 21.0.

## References
- https://medium.com/%40charlielabs101/cve-2020-12872-df315411aa70
- https://github.com/erlyaws/yaws/releases
- https://sweet32.info/
- https://github.com/erlyaws/yaws/issues/402
- https://github.com/erlyaws/yaws/blob/c0fd79f17d52628fcec527da7fa3e788c283c445/src/yaws_config.erl#L2068-L2075

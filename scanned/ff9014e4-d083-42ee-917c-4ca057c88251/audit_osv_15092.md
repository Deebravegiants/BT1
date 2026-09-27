# [H] CVE-2019-13337

## Summary
Severity: High
Advisory: CVE-2019-13337
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-13337
Type: osv

## Details
In WESEEK GROWI before 3.5.0, the site-wide basic authentication can be bypassed by adding a URL parameter access_token (this is the parameter used by the API). No valid token is required since it is not validated by the backend. The website can then be browsed as if no basic authentication is required.

## References
- https://gist.github.com/polkaman/d039fb5236a043907e44efc198d9161c

# [M] CVE-2017-2298

## Summary
Severity: Medium
Advisory: CVE-2017-2298
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-06-30
Source: https://osv.dev/vulnerability/CVE-2017-2298
Type: osv

## Details
The mcollective-sshkey-security plugin before 0.5.1 for Puppet uses a server-specified identifier as part of a path where a file is written. A compromised server could use this to write a file to an arbitrary location on the client with the filename appended with the string "_pub.pem".

## References
- https://github.com/puppetlabs/mcollective-sshkey-security/blob/0.5.1/CHANGELOG.md
- https://github.com/puppetlabs/mcollective-sshkey-security/commit/3388a3109f4fb1c69fa8505e991bf59ca20d19a2
- https://puppet.com/security/cve/cve-2017-2298

# [H] CVE-2014-5282

## Summary
Severity: High
Advisory: CVE-2014-5282
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2014-5282
Type: osv

## Details
Docker before 1.3 does not properly validate image IDs, which allows remote attackers to redirect to another image through the loading of untrusted images via 'docker load'.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1168436
- https://bugzilla.redhat.com/show_bug.cgi?id=1168436
- https://groups.google.com/forum/#%21msg/docker-announce/aQoVmQlcE0A/smPuBNYf8VwJ

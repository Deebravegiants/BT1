# [H] CVE-2016-2146

## Summary
Severity: High
Advisory: CVE-2016-2146
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-15
Source: https://osv.dev/vulnerability/CVE-2016-2146
Type: osv

## Details
The am_read_post_data function in mod_auth_mellon before 0.11.1 does not limit the amount of data read, which allows remote attackers to cause a denial of service (worker process crash, web server deadlock, or memory consumption) via a large amount of POST data.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179085.html
- https://sympa.uninett.no/lists/uninett.no/arc/modmellon/2016-03/msg00000.html
- https://github.com/UNINETT/mod_auth_mellon/pull/71

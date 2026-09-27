# [M] CVE-2021-3502

## Summary
Severity: Medium
Advisory: CVE-2021-3502
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-07
Source: https://osv.dev/vulnerability/CVE-2021-3502
Type: osv

## Details
A flaw was found in avahi 0.8-5. A reachable assertion is present in avahi_s_host_name_resolver_start function allowing a local attacker to crash the avahi service by requesting hostname resolutions through the avahi socket or dbus methods for invalid hostnames. The highest threat from this vulnerability is to the service availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1946914
- https://github.com/lathiat/avahi/issues/338

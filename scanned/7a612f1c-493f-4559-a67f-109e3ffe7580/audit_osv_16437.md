# [M] CVE-2019-6961

## Summary
Severity: Medium
Advisory: CVE-2019-6961
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-6961
Type: osv

## Details
Incorrect access control in actionHandlerUtility.php in the RDK RDKB-20181217-1 WebUI module allows a logged in user to control DDNS, QoS, RIP, and other privileged configurations (intended only for the network operator) by sending an HTTP POST to the PHP backend, because the page filtering for non-superuser (in header.php) is done only for GET requests and not for direct AJAX calls.

## References
- https://dojo.bullguard.com/dojo-by-bullguard/blog/the-gateway-is-wide-open

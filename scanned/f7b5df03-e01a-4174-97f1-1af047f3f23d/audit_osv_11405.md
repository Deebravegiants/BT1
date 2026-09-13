# [M] CVE-2017-7650

## Summary
Severity: Medium
Advisory: CVE-2017-7650
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/CVE-2017-7650
Type: osv

## Details
In Mosquitto before 1.4.12, pattern based ACLs can be bypassed by clients that set their username/client id to '#' or '+'. This allows locally or remotely connected clients to access MQTT topics that they do have the rights to. The same issue may be present in third party authentication/access control plugins for Mosquitto.

## References
- http://www.debian.org/security/2017/dsa-3865
- http://www.securityfocus.com/bid/98741
- http://mosquitto.org/2017/05/security-advisory-cve-2017-7650/
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=516765

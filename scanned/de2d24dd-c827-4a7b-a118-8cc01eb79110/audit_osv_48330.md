# [M] CVE-2017-6951

## Summary
Severity: Medium
Advisory: CVE-2017-6951
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2017-6951
Type: osv

## Details
The keyring_search_aux function in security/keys/keyring.c in the Linux kernel through 3.14.79 allows local users to cause a denial of service (NULL pointer dereference and OOPS) via a request_key system call for the "dead" type.

## References
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- http://www.securityfocus.com/bid/96943
- http://www.spinics.net/lists/keyrings/msg01845.html
- http://www.spinics.net/lists/keyrings/msg01846.html
- http://www.spinics.net/lists/keyrings/msg01849.html
- https://access.redhat.com/errata/RHSA-2017:1842

# [H] CVE-2018-1311

## Summary
Severity: High
Advisory: CVE-2018-1311
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-18
Source: https://osv.dev/vulnerability/CVE-2018-1311
Type: osv

## Details
The Apache Xerces-C 3.0.0 to 3.2.3 XML parser contains a use-after-free error triggered during the scanning of external DTDs. This flaw has not been addressed in the maintained version of the library and has no current mitigation other than to disable DTD processing. This can be accomplished via the DOM using a standard parser feature, or via SAX using the XERCES_DISABLE_DTD environment variable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AJYZUBGPVWJ7LEHRCMB5XVADQBNGURXD/
- http://www.openwall.com/lists/oss-security/2024/02/16/1
- https://lists.apache.org/thread.html/r48ea463fde218b1e4cc1a1d05770a0cea34de0600b4355315a49226b%40%3Cc-dev.xerces.apache.org%3E
- https://access.redhat.com/errata/RHSA-2020:0704
- https://access.redhat.com/errata/RHSA-2020:0702
- https://lists.debian.org/debian-lts-announce/2020/12/msg00025.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7A6WWL4SWKAVYK6VK5YN7KZP4MZWC7IY/
- https://marc.info/?l=xerces-c-users&m=157653840106914&w=2
- https://www.debian.org/security/2020/dsa-4814
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AJYZUBGPVWJ7LEHRCMB5XVADQBNGURXD/
- https://lists.apache.org/thread.html/r90ec105571622a7dc3a43b846c12732d2e563561dfb2f72941625f35%40%3Cc-users.xerces.apache.org%3E
- https://lists.apache.org/thread.html/rfeb8abe36bcca91eb603deef49fbbe46870918830a66328a780b8625%40%3Cc-users.xerces.apache.org%3E
- https://lists.apache.org/thread.html/rabbcc0249de1dda70cda96fd9bcff78217be7a57d96e7dcc8cd96646%40%3Cc-users.xerces.apache.org%3E
- https://www.oracle.com/security-alerts/cpujan2022.html

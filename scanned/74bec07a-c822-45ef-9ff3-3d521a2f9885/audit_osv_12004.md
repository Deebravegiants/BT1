# [C] CVE-2018-1000616

## Summary
Severity: Critical
Advisory: CVE-2018-1000616
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-09
Source: https://osv.dev/vulnerability/CVE-2018-1000616
Type: osv

## Details
ONOS ONOS controller version 1.13.1 and earlier contains a XML External Entity (XXE) vulnerability in onos\drivers\utilities\src\main\java\org\onosproject\drivers\utilities\XmlConfigParser.java loadxml() that can result in An adversary can remotely launch XXE attacks on ONOS controller via an OpenConfig Terminal Device.. This attack appear to be exploitable via network connectivity.

## References
- https://gerrit.onosproject.org/#/c/18894/
- http://gms.cl0udz.com/Openconfig_xxe.pdf

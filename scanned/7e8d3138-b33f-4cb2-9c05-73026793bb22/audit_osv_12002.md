# [C] CVE-2018-1000614

## Summary
Severity: Critical
Advisory: CVE-2018-1000614
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-09
Source: https://osv.dev/vulnerability/CVE-2018-1000614
Type: osv

## Details
ONOS ONOS Controller version 1.13.1 and earlier contains a XML External Entity (XXE) vulnerability in providers/netconf/alarm/src/main/java/org/onosproject/provider/netconf/alarm/NetconfAlarmTranslator.java that can result in An adversary can remotely launch advanced XXE attacks on ONOS controller without authentication.. This attack appear to be exploitable via crafted protocol message.

## References
- https://gerrit.onosproject.org/#/c/18779/
- http://gms.cl0udz.com/ONOS_Vul.pdf

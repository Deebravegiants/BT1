# [H] CVE-2012-0955

## Summary
Severity: High
Advisory: CVE-2012-0955
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2012-0955
Type: osv

## Details
software-properties was vulnerable to a person-in-the-middle attack due to incorrect TLS certificate validation in softwareproperties/ppa.py. software-properties didn't check TLS certificates under python2 and only checked certificates under python3 if a valid certificate bundle was provided. Fixed in software-properties version 0.92.

## References
- https://code.launchpad.net/~cyphermox/software-properties/lp1036839/+merge/119753
- https://launchpad.net/bugs/1036839
- https://launchpad.net/bugs/1036839
- https://code.launchpad.net/~cyphermox/software-properties/lp1036839/+merge/119753

# [M] Improper Validation of Certificate with Host Mismatch in Not Yet Commons SSL

## Summary
Severity: Medium
Advisory: GHSA-cmxj-wx9v-52qr
CVE: CVE-2014-3604
CWE: CWE-297
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cmxj-wx9v-52qr
Type: github-advisory

## Affected
- Maven: `ca.juliusdavies:not-yet-commons-ssl` — affected >=0 <0.3.15

## Details
Certificates.java in Not Yet Commons SSL before 0.3.15 does not properly verify that the server hostname matches a domain name in the subject's Common Name (CN) field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3604
- https://bugzilla.redhat.com/show_bug.cgi?id=1131803
- https://exchange.xforce.ibmcloud.com/vulnerabilities/97659
- https://github.com/victims/victims-cve-db/blob/master/database/java/2014/3604.yaml
- http://juliusdavies.ca/svn/viewvc.cgi/not-yet-commons-ssl?view=rev&revision=172
- http://rhn.redhat.com/errata/RHSA-2015-1888.html

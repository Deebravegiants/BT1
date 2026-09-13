# [C] CVE-2019-7609

## Summary
Severity: Critical
Advisory: CVE-2019-7609
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-7609
Type: osv

## Details
Kibana versions before 5.6.15 and 6.6.1 contain an arbitrary code execution flaw in the Timelion visualizer. An attacker with access to the Timelion application could send a request that will attempt to execute javascript code. This could possibly lead to an attacker executing arbitrary commands with permissions of the Kibana process on the host system.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-7609
- https://access.redhat.com/errata/RHBA-2019:2824
- https://access.redhat.com/errata/RHSA-2019:2860
- https://discuss.elastic.co/t/elastic-stack-6-6-1-and-5-6-15-security-update/169077
- https://www.elastic.co/community/security
- http://packetstormsecurity.com/files/174569/Kibana-Timelion-Prototype-Pollution-Remote-Code-Execution.html

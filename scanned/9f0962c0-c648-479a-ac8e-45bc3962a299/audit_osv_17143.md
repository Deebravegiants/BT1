# [H] CVE-2020-12850

## Summary
Severity: High
Advisory: CVE-2020-12850
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-11
Source: https://osv.dev/vulnerability/CVE-2020-12850
Type: osv

## Details
The following vulnerability applies only to the Pydio Cells Enterprise OVF version 2.0.4. Prior versions of the Pydio Cells Enterprise OVF (such as version 2.0.3) have a looser policy restriction allowing the “pydio” user to execute any privileged command using sudo. In version 2.0.4 of the appliance, the user pydio is responsible for running all the services and binaries that are contained in the Pydio Cells web application package, such as mysqld, cells, among others. This user has privileges restricted to run those services and nothing more.

## References
- http://packetstormsecurity.com/files/158002/Pydio-Cells-2.0.4-XSS-File-Write-Code-Execution.html
- https://www.coresecurity.com/advisories
- https://www.coresecurity.com/core-labs/advisories/pydio-cells-204-multiple-vulnerabilities

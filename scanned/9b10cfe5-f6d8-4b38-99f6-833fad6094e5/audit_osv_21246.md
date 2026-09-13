# [H] CVE-2021-41282

## Summary
Severity: High
Advisory: CVE-2021-41282
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-01
Source: https://osv.dev/vulnerability/CVE-2021-41282
Type: osv

## Details
diag_routes.php in pfSense 2.5.2 allows sed data injection. Authenticated users are intended to be able to view data about the routes set in the firewall. The data is retrieved by executing the netstat utility, and then its output is parsed via the sed utility. Although the common protection mechanisms against command injection (i.e., the usage of the escapeshellarg function for the arguments) are used, it is still possible to inject sed-specific code and write an arbitrary file in an arbitrary location.

## References
- https://docs.netgate.com/pfsense/en/latest/releases/22-01_2-6-0.html
- https://www.shielder.it/advisories/
- http://packetstormsecurity.com/files/166208/pfSense-2.5.2-Shell-Upload.html
- https://www.shielder.it/advisories/pfsense-remote-command-execution/

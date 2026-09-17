# [H] CVE-2017-8921

## Summary
Severity: High
Advisory: CVE-2017-8921
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-05-12
Source: https://osv.dev/vulnerability/CVE-2017-8921
Type: osv

## Details
In FlightGear before 2017.2.1, the FGCommand interface allows overwriting any file the user has write access to, but not with arbitrary data: only with the contents of a FlightGear flightplan (XML). A resource such as a malicious third-party aircraft could exploit this to damage files belonging to the user. Both this issue and CVE-2016-9956 are directory traversal vulnerabilities in Autopilot/route_mgr.cxx - this one exists because of an incomplete fix for CVE-2016-9956.

## References
- https://sourceforge.net/p/flightgear/flightgear/ci/faf872e7f71ca14c567ac7080561fc785d8d2fd0/

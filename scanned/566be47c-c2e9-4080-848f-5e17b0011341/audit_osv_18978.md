# [M] CVE-2020-5416

## Summary
Severity: Medium
Advisory: CVE-2020-5416
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-5416
Type: osv

## Details
Cloud Foundry Routing (Gorouter), versions prior to 0.204.0, when used in a deployment with NGINX reverse proxies in front of the Gorouters, is potentially vulnerable to denial-of-service attacks in which an unauthenticated malicious attacker can send specially-crafted HTTP requests that may cause the Gorouters to be dropped from the NGINX backend pool.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5416

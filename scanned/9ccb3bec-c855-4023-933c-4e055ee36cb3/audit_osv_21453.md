# [H] CVE-2021-43173

## Summary
Severity: High
Advisory: CVE-2021-43173
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-11-09
Source: https://osv.dev/vulnerability/CVE-2021-43173
Type: osv

## Details
In NLnet Labs Routinator prior to 0.10.2, a validation run can be delayed significantly by an RRDP repository by not answering but slowly drip-feeding bytes to keep the connection alive. This can be used to effectively stall validation. While Routinator has a configurable time-out value for RRDP connections, this time-out was only applied to individual read or write operations rather than the complete request. Thus, if an RRDP repository sends a little bit of data before that time-out expired, it can continuously extend the time it takes for the request to finish. Since validation will only continue once the update of an RRDP repository has concluded, this delay will cause validation to stall, leading to Routinator continuing to serve the old data set or, if in the initial validation run directly after starting, never serve any data at all.

## References
- https://www.debian.org/security/2021/dsa-5033
- https://www.debian.org/security/2022/dsa-5041
- https://www.nlnetlabs.nl/downloads/routinator/CVE-2021-43172_CVE-2021-43173_CVE-2021-43174.txt

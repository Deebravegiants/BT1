# [H] CVE-2026-37232

## Summary
Severity: High
Advisory: CVE-2026-37232
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37232
Type: osv

## Details
An issue was discovered in OpenAirInterface5G 2.4.0 (nr-softmodem) in the E2SM-KPM RAN Function's PRB utilization metric calculation. The functions fill_RRU_PrbTotDl() and fill_RRU_PrbTotUl() in openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_kpm_subs.c (lines 182 and 197) compute PRB usage percentages by dividing by the difference of two consecutive total_prb_aggregate samples without checking for zero. When a malicious xApp sends a high volume of E42_RIC_SUBSCRIPTION_REQUESTs via the FlexRIC iApp (port 36422/SCTP), the E2 Agent generates KPM Indication reports at high frequency. If two consecutive sampling intervals yield identical PRB aggregate values, the divisor becomes zero, triggering SIGFPE and crashing the entire 5G base station process (nr-softmodem). This results in complete 5G cell service interruption for all connected UEs. No authentication is required.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37232.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37232.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37232
- https://gitlab.eurecom.fr/oai/openairinterface5g

# [H] CVE-2022-32778

## Summary
Severity: High
Advisory: CVE-2022-32778
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-32778
Type: osv

## Details
An information disclosure vulnerability exists in the cookie functionality of WWBN AVideo 11.6 and dev master commit 3f7c0364. The session cookie and the pass cookie miss the HttpOnly flag, making them accessible via JavaScript. The session cookie also misses the secure flag, which allows the session cookie to be leaked over non-HTTPS connections. This could allow an attacker to steal the session cookie via crafted HTTP requests.This vulnerability is for the pass cookie, which contains the hashed password and can be leaked via JavaScript.

## References
- https://github.com/WWBN/AVideo/blob/e04b1cd7062e16564157a82bae389eedd39fa088/updatedb/updateDb.v12.0.sql
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1542
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32778.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32778

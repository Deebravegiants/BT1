# [H] CVE-2024-39721

## Summary
Severity: High
Advisory: CVE-2024-39721
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-31
Source: https://osv.dev/vulnerability/CVE-2024-39721
Type: osv

## Details
An issue was discovered in Ollama before 0.1.34. The CreateModelHandler function uses os.Open to read a file until completion. The req.Path parameter is user-controlled and can be set to /dev/random, which is blocking, causing the goroutine to run infinitely (even after the HTTP request is aborted by the client).

## References
- https://github.com/ollama/ollama/blob/9164b0161bcb24e543cba835a8863b80af2c0c21/server/routes.go#L557
- https://github.com/ollama/ollama/blob/adeb40eaf29039b8964425f69a9315f9f1694ba8/server/routes.go#L536
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39721.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39721
- https://www.oligo.security/blog/more-models-more-probllms

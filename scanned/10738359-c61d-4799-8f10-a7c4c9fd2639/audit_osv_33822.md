# [C] CVE-2025-50900

## Summary
Severity: Critical
Advisory: CVE-2025-50900
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-50900
Type: osv

## Details
An issue was discovered in getrebuild/rebuild 4.0.4. The affected source code class is com.rebuild.web.RebuildWebInterceptor, and the affected function is preHandle In the filter code, use CodecUtils.urlDecode(request.getRequestURI()) to obtain the URL-decoded request path, and then determine whether the path endsWith /error. If so, execute return true to skip this Interceptor. Else, redirect to /user/login api. Allowing unauthenticated attackers to gain sensitive information or escalated privileges.

## References
- https://racerz.notion.site/Rebuild-Vulnerability-1ede0e0074f280d8a906c38442a393f0
- https://www.notion.so/racerz/Rebuild-Vulnerability-1ede0e0074f280d8a906c38442a393f0?pvs=4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50900.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50900

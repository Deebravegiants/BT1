# [M] iris-web vulnerable to Server Side Template Injection in reports

## Summary
Severity: Medium
Advisory: CVE-2024-25624
Aliases: GHSA-m64w-f7fg-hpcr
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-25624
Type: osv

## Details
Iris is a web collaborative platform aiming to help incident responders sharing technical details during investigations. Due to an improper setup of Jinja2 environment, reports generation in `iris-web` is prone to a Server Side Template Injection (SSTI). Successful exploitation of the vulnerability can lead to an arbitrary Remote Code Execution. An authenticated administrator has to upload a crafted report template containing the payload. Upon generation of a report based on the weaponized report, any user can trigger the vulnerability.  The vulnerability is patched in IRIS v2.4.6. No workaround is available. It is recommended to update as soon as possible. Until patching, review the report templates and keep the administrative privileges that include the upload of report templates limited to dedicated users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25624.json
- https://github.com/dfir-iris/iris-web/security/advisories/GHSA-m64w-f7fg-hpcr
- https://nvd.nist.gov/vuln/detail/CVE-2024-25624

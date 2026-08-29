# [C] Remote Command Execution via Github import

## Summary
Severity: Critical (CVSS 9.9)
Program: GitLab
Weakness: Command Injection - Generic
Reporter: vakzz
State: resolved
Disclosed: 2022-10-06T20:19:24.594Z
CVE: CVE-2022-2884
Source: https://hackerone.com/reports/1679624

## Details
### Summary

This is very similar to https://about.gitlab.com/releases/2022/08/22/critical-security-release-gitlab-15-3-1-released/#Remote%20Command%20Execution%20via%20Github%20import and allows arbitrary redis commands to be injected when imported a GitHub repository.

When importing a GitHub repo the api client uses `Sawyer` for handling the responses. This takes a json hash and converts it into a ruby class that has methods matching all of the keys:

https://github.com/lostisland/sawyer/blob/v0.9.2/lib/sawyer/resource.rb#L106-L110
```ruby
    def self.attr_accessor(*attrs)
      attrs.each do |attribute|
        class_eval do
          define_method attribute do
            @attrs[attribute.to_sym]
          end

          define_method "#{attribute}=" do |value|
            @attrs[attribute.to_sym] = value
          end

          define_method "#{attribute}?" do
            !!@attrs[attribute.to_sym]
          end
        end
      end
    end
```

This happens recursively, and allows for any method to be overridden including built-in methods such as `to_s`.

The redis gem uses `to_s` and `bytesize` to generate the RESP command, so if a `Sawyer::Resource` is ever passed in that has a controllable hash it can allow arbitrary redis commands to be injected into the stream as the string will be shorter than the `$` size provided (see https://redis.io/docs/reference/protocol-spec/)

https://github.com/redis/redis-rb/blob/v4.4.0/lib/redis/connection/command_helper.rb#L20
```ruby
            i = i.to_s
            command << "$#{i.bytesize}"
            command << i
```


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1679624_

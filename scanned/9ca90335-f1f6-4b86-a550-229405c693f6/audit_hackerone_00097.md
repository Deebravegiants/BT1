# [C] RCE via github import

## Summary
Severity: Critical (CVSS 9.9)
Program: GitLab
Weakness: OS Command Injection
Reporter: yvvdwf
State: resolved
Disclosed: 2022-11-16T01:10:35.826Z
Source: https://hackerone.com/reports/1672388

## Details
Hello,

While continuing mining on [github import](https://hackerone.com/reports/1665658), I found a vulnerability on gitlab.com allowing to execute remotely arbitrary commands.

Gitlab uses Octokit to get data from github.com. Octokit uses [Sawyer::Resource](https://github.com/lostisland/sawyer/blob/master/lib/sawyer/resource.rb) to represent results.

Sawyer is a crazy class that [converts](https://github.com/lostisland/sawyer/blob/f5f080d5c5260e094069139ffc7c13d0acba4ab5/lib/sawyer/resource.rb#L81) a hash to an object whose methods are based on the hash's key:

```ruby
irb(main):641:0> Sawyer::VERSION
=> "0.8.2"
irb(main):642:0> a = Sawyer::Resource.new( Sawyer::Agent.new(""), to_s: "example", length: 1)
=> 
{:to_s=>"example", :length=>1}
...
irb(main):643:0> a.to_s
=> "example"
irb(main):644:0> a.length
=> 1
```

Gitlab uses directly the responded Sawyer object in few functions, such as, the `id` variable in [this function](https://gitlab.com/gitlab-org/gitlab/-/blob/99f5db917a33ad9466f35918a1da454ed397be8e/lib/gitlab/github_import/parallel_scheduling.rb#L145):

```ruby
      def already_imported?(object)
        id = id_for_already_imported_cache(object)

        Gitlab::Cache::Import::Caching.set_includes?(already_imported_cache_key, id)
      end
```

Normally, `id` should be a number. However when `id` is `{"to_s": {"bytesize": 2, "to_s": "1234REDIS_COMMANDS" }}`, we can inject additional redis commands by using `bytesize` to limit the previous command when it [is constructed](https://github.com/redis/redis-rb/blob/v4.4.0/lib/redis/connection/command_helper.rb#L8) (although the `bytesize` is `2` we need to reserve 4 bytes as 2 additional bytes for CLRF):

```ruby
      def build_command(args)
        command = [nil]

        args.each do |i|
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1672388_

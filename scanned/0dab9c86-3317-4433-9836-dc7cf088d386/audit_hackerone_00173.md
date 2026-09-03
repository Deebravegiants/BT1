# [M] Regular expression denial of service in ActiveRecord's PostgreSQL Money type

## Summary
Severity: Medium (CVSS 5.3)
Program: Ruby on Rails
Weakness: Uncontrolled Resource Consumption
Reporter: dee-see
State: resolved
Disclosed: 2021-02-11T00:13:07.326Z
CVE: CVE-2021-22880
Source: https://hackerone.com/reports/1023899

## Details
## Summary

Hello team! The regular expressions used in the [Money](https://github.com/rails/rails/blob/ddd0e9b/activerecord/lib/active_record/connection_adapters/postgresql/oid/money.rb#L29) type to convert strings like `-$100,000.00` to `100000` have an execution time with a quadratic growth proportional to the length of the string.

Causing the denial of service requires very long strings but if the parameter is in a post body that won't be a problem.

## Details

The regular expressions marked `(1)` and `(2)` in [the following code](https://github.com/rails/rails/blob/ddd0e9b/activerecord/lib/active_record/connection_adapters/postgresql/oid/money.rb#L28-L33) are the vulnerable expressions

```ruby
            case value
            when /^-?\D*[\d,]+\.\d{2}$/  # (1)
              value.gsub!(/[^-\d.]/, "")
            when /^-?\D*[\d.]+,\d{2}$/  # (2)
              value.gsub!(/[^-\d,]/, "").sub!(/,/, ".")
            end
```

This code is invoked when Rails saves a user-input value in a `Money` field. If we look at the first expression, the problem comes from this bit `\D*[\d,]+`. It matches "not a number" 0 or more times and then "a number or a ," one or more times. The `,` can match both expressions so this is somewhat equivalent to `,*,+` as far as the attack is concerned and is where the `O(n^2)` execution time comes from.

## Steps to reproduce

I'm going to assume PostgreSQL is installed and configured on the machine.

Now we'll install the PostgreSQL ruby interface, setup a rails application and scaffold a view for the attack.

```ruby
gem install pg
rails new moneydos --database=postgresql
cd moneydos
rails db:setup
rails g scaffold Money amount:money
rake db:migrate
```

Now in the `rails console` run these commands. (The same could be accomplished though the UI, but this is simpler for reproduction purpose)


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1023899_

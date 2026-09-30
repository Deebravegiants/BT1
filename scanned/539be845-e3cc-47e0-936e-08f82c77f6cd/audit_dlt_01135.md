# [C] rest-client Gem Contains Malicious Code

## Summary
Severity: Critical
Chain: rest-client
Component: rest-client, cron_parser, cron_parser, coin_base, blockchain_wallet, awesome-bot, doge-coin, capistrano-colors, bitcoin_
CVE: CVE-2019-15224
CWE: Improper Control of Generation of Code ('Code Injection')
Published: 2019-08-20
Source: https://github.com/advisories/GHSA-333g-rpr4-7hxq
Type: github-advisory

## Details
The rest-client gem 1.6.10 through 1.6.13 for Ruby, as distributed on RubyGems.org, included a code-execution backdoor inserted by a third party.
Users of an affected version should consider downgrading to the last non-affected version of 1.6.9, or upgrading to 1.7.x.
Additionally, a set of other minor gems have been partially or completely yanked and are included in this advisory.
These include cron_parser, coin_base, blockchain_wallet, awesome-bot, doge-coin, capistrano-colors, bitcoin_vanity, lita_coin, coming-soon, and omniauth_amazon.

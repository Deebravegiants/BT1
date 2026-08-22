# [M] [api.tumblr.com] Denial of Service by cookies manipulation

## Summary
Severity: Medium (CVSS 4.9)
Program: Automattic
Weakness: Uncontrolled Resource Consumption
Reporter: fuzzme
State: resolved
Disclosed: 2020-11-29T10:48:55.466Z
Source: https://hackerone.com/reports/1005421

## Details
Hello

## Summary:

I have found at api.tumblr.com two parameters ```consumer_key ``` &&  ```consumer_secret``` allow to modify ```oa-consumer_key```  && ```oa_consumer_secret```  cookies values and property.

An attacker can send a malicious link to reset the cookies of api.tumblr.com, this lead to DOS.
To trigger the DOS, the target/victim account need to click a malicious link.

To restore the account, the victim need to delete all cookies on api.tumblr.com.

Similar issues :  https://hackerone.com/reports/583819

##Vulnerable Url

```
https://api.tumblr.com/console/auth?
```

##Vulnerable Paramater(s)

```
$_GET['consumer_key'];
$_GET['consumer_secret'];
$_POST['consumer_key'];
$_POST['consumer_secret'];
```
## Steps To Reproduce:

1. Login at https://www.tumblr.com/

2. Go to https://www.tumblr.com/oauth/apps and create a random application

/!\ if the cookies "oa-consumer_key" && "oa_consumer_secret" already exist the attack doesn't  work /!\

3. After, create your application, click to this malicious following link 
```
https://api.tumblr.com/console/auth?consumer_key=x;%20domain=tumblr.com;%20Max-Age=1000000000000000000000&consumer_secret=x;%20domain=tumblr.com;%20Max-Age=1000000000000000000000
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1005421_

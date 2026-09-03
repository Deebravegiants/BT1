# [M] Server-Side Request Forgery (SSRF) in Ghost CMS 

## Summary
Severity: Medium (CVSS 4.4)
Program: Node.js third-party modules
Weakness: Server-Side Request Forgery (SSRF)
Reporter: whoareme
State: resolved
Disclosed: 2020-03-09T12:21:11.600Z
CVE: CVE-2020-8134
Source: https://hackerone.com/reports/793704

## Details
I would like to report about SSRF vulnerability in CMS Ghost blog

It allows attacker able to send a crafted GET request from a vulnerable web application

# Module

**module name:** ghost
**version:** 3.5.2
**npm page:** `https://www.npmjs.com/package/ghost`
**website page** `https://ghost.org/`

## Module Description

Ghost is the world’s most popular open source headless Node.js CMS. 

## Module Stats

4,812 weekly downloads

This CMS is used around 512,000 times for creating Blogs in 2018 according to Ghost statics. Currently the biggest customers of this blog are: Apple, Elon Musk's OpenAI team, Tinder, DigitalOcean, DuckDuckGo, Mozilla, Airtable, Revolt, etc.

# Vulnerability
Attacker with publisher role (editor, author, contributor, administrator) in a blog may be able to leverage this to make arbitrary GET requests in a CMS Ghost Blog instance's to internal / external network.

## Vulnerability Description
CMS Ghost allows publishers to set up embed content from many sources (like Youtube, Twitter, Instagram, etc).
F713079

When click you click on the “Other…” button you can see the following input.
F713080
This input are send request to the route which is vulnerable for the SSRF attack. Let's discover it! 
When you try to pass some URL into this input we receive response like that:
```
GET /ghost/api/v3/admin/oembed/?url=http://169.254.169.254/metadata/v1.json&type=embed
```
F713081
In my case I trying to receive DigitalOcean MetaData from my server.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/793704_

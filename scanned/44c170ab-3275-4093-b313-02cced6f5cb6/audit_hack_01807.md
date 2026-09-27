# [M] S3 Buckets Cleartext Communication

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The system's S3 buckets are configured to allow unencrypted traffic:

```
$ curl -v http://fei.money.s3.amazonaws.com/index.html
*   Trying 52.219.112.162:80...
* TCP_NODELAY set
* Connected to fei.money.s3.amazonaws.com (52.219.112.162) port 80 (0)
> GET /index.html HTTP/1.1
> Host: fei.money.s3.amazonaws.com
> User-Agent: curl/7.68.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< x-amz-id-2: 0QtzqEhGn7gHUjjiAxpniOMXKQ1O1ouT6Tp8iQG2EfvlKbg0ZgEbDdkQrJrJL2OyJF1VyZkPjjU=
< x-amz-request-id: D6250FE8F76E84F0
< Date: Tue, 09 Feb 2021 13:07:54 GMT
< Last-Modified: Mon, 11 Jan 2021 20:38:09 GMT
< ETag: "ec826fa83693f3db3a989fcbeb5adef1"
< Accept-Ranges: bytes
< Content-Type: text/html
< Content-Length: 3675
< Server: AmazonS3
< 
< ...
```

#### Affected Assets

- `arn:aws:s3:::ropsten-app.fei.money/*`
- `arn:aws:s3:::www.fei.money/*`
- `arn:aws:s3:::feiprotocol.com/*`
- `arn:aws:s3:::www.app.fei.money/*`
- `arn:aws:s3:::www.ropsten-app.fei.money/*`
- `arn:aws:s3:::app.fei.money/*`
- `arn:aws:s3:::fei.money/*`

#### Recommendation

It is recommended to enforce encryption of data in transit using TLS certificates. To accomplish this, the `aws:SecureTransport` can be set in the S3 bucket's policies.

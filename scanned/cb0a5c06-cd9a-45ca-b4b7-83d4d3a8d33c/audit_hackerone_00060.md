# [M] Misconfiguration in AWS CloudFront CDN configuration makes rubygems.org serve (and cache) content from a unclaimed S3-bucket

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Misconfiguration
Reporter: p4fg
State: resolved
Disclosed: 2023-12-07T14:57:26.668Z
Source: https://hackerone.com/reports/2262939

## Details
This is reported as suggested by the rubygems-program on hackerone. 
Report: https://hackerone.com/reports/2256740

I stumbled on the URL `https://rubygems.org/names`

That was giving the following response:
```xml
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<Error>
<Code>NoSuchBucket</Code>
<Message>The specified bucket does not exist</Message>
<BucketName>index.rubygems.org</BucketName>
<RequestId>KF8VDAZNXRZ3S9YQ</RequestId>
<HostId>MgMX9WXs1oJ0Rx8ABtxR+6UHFgVLyoqwqy/CRRPVMjlPLuSFdebn3E2L/8b7ZDL8QyF56JFL004=</HostId>
</Error>
```

Claiming the bucket in `index.rubygems.org` in region `us-east-2` gives a different error on the url `https://rubygems.org/names` indicating that the cloudfront-configuration tries to access the bucket using the wrong region:
```xml
<Error>
<Code>TemporaryRedirect</Code>
<Message>Please re-send this request to the specified temporary endpoint. Continue to use the original request endpoint for future requests.</Message>
<Endpoint>index.rubygems.org.s3.us-east-2.amazonaws.com</Endpoint>
<Bucket>index.rubygems.org</Bucket>
<RequestId>6AFP30FTX2AF5FEM</RequestId>
<HostId>BAVFkSyL0+Y7oMTL8li45vFTb0UCtSVB/pPFFQvRrSf8cSVAURS0SLjeb58XZ+E8me8Crw8jVKc=</HostId>
</Error>
```
Claiming the bucket `index.rubygems.org` in region `us-west-2` makes the endpoint start returning data from a file named `names` in the bucket, using the content-type specified by me on the file in the bucket. 
This response will be cached by Cloudfront for quite some time, so in the logs (below) only the cache-misses are logged.

## Impact

This bug would allow me to set the content-type using AWS S3 CLI to text/html and serve stored XSS on the page. This could affect a logged in maintainer in a very bad way.

I could also affect the availability for connected systems that relied on the list of names for CI-pipelines (for example).

Several artifactory instances were also observed in the S3-logs trying to access files from the bucket, this is just a sample:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2262939_

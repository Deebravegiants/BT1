### Title
Unbounded, zero-backoff retry loop in PCP biometric upload risks self-inflicted rate limiting / backend ban - (File: src/agents/data_uploader.rs)

### Summary
`Agent::upload_pcp` in `src/agents/data_uploader.rs` retries failed personal custody package (PCP, i.e. biometric iris/face data) uploads to the backend in a tight, unbounded `loop` with **no sleep, no exponential backoff, and no `Retry-After` handling** whenever the failure is not a 4xx client error [1](#0-0) . This mirrors the exact bug class described in the external report: a client that keeps hammering a backend API after receiving repeated errors, with no throttling logic, risking rate limiting or an outright ban of the Orb by the backend/WAF.

### Finding Description
The upload retry loop is:

```rust
loop {
    let response = backend::upload_personal_custody_package::request(...).await;
    match response {
        Ok(()) => { ... break; }
        Err(err) => {
            tracing::error!(...);
            dd_incr!(...);
            if let Some(reqwest_err) = err.downcast_ref::<reqwest::Error>() {
                if let Some(status) = reqwest_err.status() {
                    if status.is_client_error() { ... break; }
                }
            }
            // otherwise: loop again immediately, no delay
        }
    }
}
``` [1](#0-0) 

Key issues:
- Any failure that is **not** an HTTP 4xx (e.g., network errors, timeouts, connection resets, 5xx server errors, or transient WAF/CDN throttling responses) causes an immediate re-request with zero delay — there is no `sleep`, jitter, or backoff of any kind between attempts, and no maximum retry cap, unlike the bounded, sleep-gated retry logic used elsewhere for signup polling (`RETRIES_COUNT` / `POLL_STATUS_INTERVAL` in `src/plans/enroll_user.rs`) [2](#0-1) .
- This loop runs per-package inside `FuturesUnordered` with up to `PARALLEL_UPLOAD_STREAMS` (4) concurrent uploaders per data-uploader agent instance [3](#0-2) [4](#0-3) , so a persistent backend outage or degraded connectivity condition (very plausible in field-deployed hardware) turns into a sustained, high-frequency request storm against `backend::upload_personal_custody_package::request`, which itself first requests a presigned URL from `presigned_url::request_package`/`request_tiered_package` and then PUTs data to S3 [5](#0-4) .
- The shared `client()`/`client_with_timeouts()` builder used for all backend calls has no rate-limiting, circuit-breaker, or backoff wrapper at all — it only sets simple timeouts [6](#0-5) .
- Conversely, when the response actually is a 4xx client error (which would include HTTP 429, since `reqwest`'s `is_client_error()` covers the 400-499 range), the code treats it as terminal and drops the biometric package permanently rather than honoring `Retry-After` or backing off and retrying later. So the flow is broken in both directions: it either retries forever with no delay (5xx/network) or gives up immediately on the first 429/4xx with no recovery.

This is a direct analog to the reported bug class (price-feeder hammering exchange APIs without honoring 429/backoff), reachable by any operator/user performing a normal signup — no privileged or malicious-peer access is required.

### Impact Explanation
Because biometric package upload (`upload_pcp`) is part of the standard, unprivileged signup flow, any transient backend degradation (which is common for field devices on cellular/WiFi links) causes the Orb to enter a busy-loop of immediate re-requests to the signup/data backend. This can:
- Trigger IP-based or per-orb-token rate limiting/temporary bans from the backend or its edge/WAF layer, in line with the ToB report's exact scenario, potentially escalating to a **permanent ban** of the Orb's credentials/IP if sustained.
- Starve other concurrent uploads and the four-slot parallel upload pool (`PARALLEL_UPLOAD_STREAMS`), degrading or blocking biometric data upload/retention for the affected and subsequent signups.
- Permanently drop legitimate biometric custody packages when the backend momentarily returns 429 (client_error path breaks immediately), causing silent data loss / incomplete signup persistence without any user-facing recovery, since the upload result is fire-and-forget from the data-uploader queue's perspective once the loop exits.

### Likelihood Explanation
Any normal signup that experiences intermittent connectivity or a backend hiccup (a near-certain occurrence over the life of many field-deployed orbs) will hit this exact loop. No attacker action or privilege escalation is needed — it is a reliability/availability defect reachable purely through the standard unprivileged signup → PCP upload path.

### Recommendation
- Add exponential backoff with jitter and a bounded maximum retry count to the retry loop in `upload_pcp`, similar to the pattern already used for `signup_post`/`signup_poll` (`RETRIES_COUNT`, `POLL_STATUS_INTERVAL`) [2](#0-1) .
- Explicitly detect HTTP 429 and honor any `Retry-After` header before retrying, instead of lumping it in with generic terminal 4xx handling.
- Distinguish transient 5xx/network errors (retry with backoff) from non-retriable 4xx errors, and persist/report packages that are ultimately dropped so operators/backends are aware of data loss.
- Apply the same review across other backend request call sites (`upload_image.rs`, `upload_debug_report.rs`, `presigned_url.rs`) to ensure consistent rate-limit-aware retry behavior [7](#0-6) [8](#0-7) .

### Proof of Concept
1. Simulate the backend endpoint used by `backend::upload_personal_custody_package::request` returning HTTP 503 (or a connection timeout) repeatedly for a given signup's PCP tier upload.
2. Observe that `Agent::upload_pcp` in `src/agents/data_uploader.rs` (lines 176-215) re-issues the request in a tight loop with no delay between attempts, driven purely by however fast the mocked/backend server responds — confirming the absence of backoff/rate-limit handling.
3. Repeat with a mocked HTTP 429 response with a `Retry-After` header: observe the code treats it as a terminal client error and drops the package on the very first attempt (breaks out of the loop) rather than waiting and retrying — confirming legitimate data loss under transient rate limiting.

### Citations

**File:** src/agents/data_uploader.rs (L22-22)
```rust
const PARALLEL_UPLOAD_STREAMS: usize = 4;
```

**File:** src/agents/data_uploader.rs (L105-132)
```rust
        let mut queues: [_; TIERS_COUNT as usize] = array::from_fn(|_| Queue::new_memory());
        let mut uploaders = FuturesUnordered::new();
        let mut waiters = Vec::<oneshot::Sender<()>>::new();
        let check_blocking = |queues: &[Queue]| -> bool {
            for (i, queue) in queues.iter().enumerate() {
                if queue.len() >= blocking_thresholds[i] as usize {
                    return true;
                }
            }
            false
        };
        loop {
            select! {
                biased;
                Some((tier, id)) = uploaders.next() => {
                    queues[usize::from(tier - 1)].commit(id).await;
                    if !check_blocking(&queues) {
                        for tx in take(&mut waiters) {
                            tx.send(()).unwrap();
                        }
                    }
                    for queue in &mut queues {
                        if let Some((pcp, id)) = queue.pop().await {
                            log_queues!(queues);
                            uploaders.push(self.upload_pcp(pcp, id));
                            break;
                        }
                    }
```

**File:** src/agents/data_uploader.rs (L176-215)
```rust
        loop {
            let response = backend::upload_personal_custody_package::request(
                &signup_id,
                &user_id,
                checksum.as_ref(),
                &data,
                Some(tier),
                &self.config,
            )
            .await;
            match response {
                Ok(()) => {
                    dd_timing!("main.time.signup.upload_custody_images" + format!("t{}", tier), t);
                    tracing::info!(
                        "Personal custody package tier {tier} uploading completed in: {}ms",
                        t.elapsed().as_millis()
                    );
                    break;
                }
                Err(err) => {
                    tracing::error!("UPLOAD PERSONAL CUSTODY PACKAGE TIER {tier} ERROR: {err:?}");
                    dd_incr!(
                        "main.count.http.upload_custody_images.error.network_error",
                        "error_type:normal"
                    );
                    if let Some(reqwest_err) = err.downcast_ref::<reqwest::Error>() {
                        if let Some(status) = reqwest_err.status() {
                            if status.is_client_error() {
                                dd_incr!(
                                    "main.count.signup.result.failure.upload_custody_images",
                                    "type:network_error",
                                    "subtype:signup_request"
                                );
                                break;
                            }
                        }
                    }
                }
            }
        }
```

**File:** src/plans/enroll_user.rs (L91-102)
```rust
        for i in 0..RETRIES_COUNT {
            let response = signup_post::request(
                signature.as_ref(),
                &signup_id,
                &self.operator_qr_code,
                &self.user_qr_code,
                &self.s3_region_str,
                self.capture,
                self.pipeline,
                self.signup_reason,
            )
            .await;
```

**File:** src/backend/upload_personal_custody_package.rs (L16-68)
```rust
pub async fn request(
    signup_id: &SignupId,
    session_id: &str,
    checksum: &[u8],
    data: &[u8],
    tier: Option<u8>,
    config: &Arc<Mutex<Config>>,
) -> Result<()> {
    let t0 = Instant::now();
    let presigned_url::Response { url: presigned_url, fields: form_data_params } =
        if let Some(tier) = tier {
            presigned_url::request_tiered_package(
                &DATA_BACKEND_URL,
                signup_id,
                session_id,
                &BASE64.encode(checksum),
                tier,
            )
            .await?
        } else {
            presigned_url::request_package(
                &DATA_BACKEND_URL,
                signup_id,
                session_id,
                &BASE64.encode(checksum),
            )
            .await?
        };
    dd_timing!("main.time.signup.upload_custody_images.presigned", t0);
    tracing::debug!("Images self-custody presigned_url: {presigned_url:?}");
    tracing::debug!("Images self-custody form_data_params: {form_data_params:?}");
    let file = Part::bytes(data.to_vec())
        .file_name("package.tar.gz")
        .mime_str("application/octet-stream")?;
    let form = form_data_params
        .into_iter()
        .flatten()
        .fold(Form::new(), |form, (key, value)| form.text(key, value))
        .part("file", file);
    let Config { backend_http_connect_timeout, backend_http_request_timeout, .. } =
        *config.lock().await;
    let request =
        super::client_with_timeouts(backend_http_connect_timeout, backend_http_request_timeout)?
            .post(presigned_url)
            .multipart(form);
    tracing::debug!("Sending request {request:#?}");
    let t1 = Instant::now();
    let response = request.send().await?;
    dd_timing!("main.time.signup.upload_custody_images.upload", t1);
    tracing::debug!("Received response {response:#?}");
    response.error_for_status()?;
    Ok(())
}
```

**File:** src/backend/mod.rs (L24-38)
```rust
pub fn client() -> reqwest::Result<reqwest::Client> {
    client_with_timeouts(REQUEST_TIMEOUT, CONNECT_TIMEOUT)
}

/// Creates a new HTTPS client with custom timeouts.
pub fn client_with_timeouts(
    request_timeout: Duration,
    connect_timeout: Duration,
) -> reqwest::Result<reqwest::Client> {
    orb_security_utils::reqwest::http_client_builder()
        .user_agent(APP_USER_AGENT)
        .timeout(request_timeout)
        .connect_timeout(connect_timeout)
        .build()
}
```

**File:** src/backend/upload_image.rs (L16-36)
```rust
pub async fn request(
    signup_id: &SignupId,
    image_id: &ImageId,
    presigned_url_type: UrlType,
    img_data: Vec<u8>,
    dd_image_type: &str,
) -> Result<()> {
    let t: Instant = Instant::now();
    let presigned_url::Response { url: presigned_url, .. } =
        presigned_url::request(&DATA_BACKEND_URL, signup_id, Some(image_id), presigned_url_type)
            .await?;
    dd_timing!("main.time.data_acquisition.upload" + format!("{}.presigned", dd_image_type), t);
    tracing::debug!("Image presigned_url: {:?}", presigned_url);
    let request =
        super::client()?.put(presigned_url).header(CONTENT_LENGTH, img_data.len()).body(img_data);
    let t = Instant::now();
    let response = request.send().await?;
    dd_timing!("main.time.data_acquisition.upload" + format!("{}.upload", dd_image_type), t);
    response.error_for_status()?;
    Ok(())
}
```

**File:** src/backend/presigned_url.rs (L90-129)
```rust
/// Request a presigned url
pub async fn request(
    backend_url: &str,
    signup_id: &SignupId,
    image_id: Option<&ImageId>,
    url_type: UrlType,
) -> Result<Response> {
    let image_id = image_id.map(ToString::to_string).unwrap_or_default();
    let endpoint = match url_type {
        UrlType::Ir
        | UrlType::Rgb
        | UrlType::Thermal
        | UrlType::IrFace
        | UrlType::Tof2dIr
        | UrlType::Tof2dDepth
        | UrlType::NormalizedIrisImage
        | UrlType::NormalizedIrisMask => {
            format!("{backend_url}/api/v2/signups/{signup_id}/upload")
        }
        UrlType::Metadata | UrlType::Tof2dConfidence | UrlType::Tof2dNoise => {
            format!("{backend_url}/api/v1/signups/{signup_id}/upload")
        }
    };
    let request = super::client()?.post(endpoint).basic_auth(&*ORB_ID, Some(get_orb_token()?));
    let request = request.json(&Request { url_type, orb_id: ORB_ID.as_str(), image_id: &image_id });
    tracing::debug!("Sending request {request:#?}");
    let response = request.send().await?;
    match response.error_for_status_ref() {
        Ok(_) => {
            let response = response.json::<Response>().await?;
            tracing::debug!("Received response {response:#?}");
            Ok(response)
        }
        Err(err) => {
            let response = response.text().await?;
            tracing::error!("Received error response {err:#?} with body: {response}");
            Err(err.into())
        }
    }
}
```
